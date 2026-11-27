from collections.abc import Generator
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.sessions import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    read_session_token,
    validate_csrf_token,
)
from app.db.models import User
from app.infrastructure.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    request: Request,
    session: Session = Depends(get_db),
) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    user_id = read_session_token(token) if token else None
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user = session.get(User, user_id)
    if user is None or user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return user


def require_roles(*allowed_roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if not set(user.role_codes or []).intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return user

    return dependency


def require_csrf(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    origin = request.headers.get("origin")
    if origin and origin not in set(get_settings().cors_origins):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin.",
        )

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get("X-CSRF-Token")
    if (
        not cookie_token
        or not header_token
        or cookie_token != header_token
        or not validate_csrf_token(user.id, header_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )
    return user
