from datetime import UTC, datetime

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_csrf
from app.core.config import get_settings
from app.core.passwords import verify_password
from app.core.sessions import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_csrf_token,
    create_session_token,
)
from app.db.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class StaffLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


def _cookie_secure() -> bool:
    return get_settings().app_env.lower() not in {"development", "test"}


def _set_auth_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(user.id),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=_cookie_secure(),
        httponly=False,
        samesite="strict",
    )


def _check_login_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in set(get_settings().cors_origins):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin.",
        )


def _google_client():
    settings = get_settings()
    if not settings.google_oauth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Set the Google OAuth environment variables.",
        )

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret.get_secret_value(),
        server_metadata_url=(
            "https://accounts.google.com/.well-known/openid-configuration"
        ),
        client_kwargs={
            "scope": "openid email profile",
            "code_challenge_method": "S256",
        },
    )
    return oauth.create_client("google")


@router.post("/staff/login")
def staff_login(
    payload: StaffLoginRequest,
    request: Request,
    response: Response,
    session: Session = Depends(get_db),
) -> dict[str, object]:
    _check_login_origin(request)
    normalized_email = payload.email.strip().casefold()
    user = session.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )
    if (
        user is None
        or user.account_status != "ACTIVE"
        or not set(user.role_codes or []).intersection({"ADMIN", "RECEIVER"})
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user.last_login_at = datetime.now(UTC)
    session.commit()
    _set_auth_cookie(response, user)
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role_codes": user.role_codes,
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)) -> dict[str, object]:
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "role_codes": user.role_codes,
        "auth_provider": user.auth_provider,
    }


@router.get("/csrf")
def issue_csrf_token(
    response: Response,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    token = create_csrf_token(user.id)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        max_age=60 * 60,
        httponly=False,
        secure=_cookie_secure(),
        samesite="strict",
        path="/",
    )
    return {"csrf_token": token}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    user: User = Depends(require_csrf),
) -> Response:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        secure=_cookie_secure(),
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=_cookie_secure(),
        httponly=False,
        samesite="strict",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/google")
async def google_login(request: Request):
    google = _google_client()
    return await google.authorize_redirect(
        request,
        get_settings().google_redirect_uri,
    )


@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    session: Session = Depends(get_db),
):
    google = _google_client()
    try:
        token = await google.authorize_access_token(request)
        userinfo = token.get("userinfo") or {}
    except Exception:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google sign-in could not be completed.",
        ) from None

    subject = userinfo.get("sub")
    email = userinfo.get("email")
    if not subject or not email or userinfo.get("email_verified") is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google did not provide a verified account identity.",
        )

    user = session.scalar(
        select(User).where(
            User.auth_provider == "GOOGLE",
            User.provider_subject == subject,
        )
    )
    if user is None:
        user = User(
            auth_provider="GOOGLE",
            provider_subject=subject,
            email=str(email).strip().casefold(),
            display_name=str(userinfo.get("name") or email)[:150],
            avatar_url=userinfo.get("picture"),
            role_codes=["CITIZEN"],
            account_status="ACTIVE",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    if user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not active.",
        )

    user.last_login_at = datetime.now(UTC)
    session.commit()
    response = RedirectResponse(
        url="/citizen",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    _set_auth_cookie(response, user)
    request.session.clear()
    return response
