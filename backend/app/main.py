from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.attachments import router as attachments_router
from app.api.dashboard import router as dashboard_router
from app.api.datasets import router as datasets_router
from app.api.health import router as health_router
from app.api.models import router as model_router
from app.api.reports import (
    admin_router as admin_reports_router,
    catalog_router,
    citizen_router,
)
from app.core.config import get_settings
from app.core.sessions import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    read_session_token,
    validate_csrf_token,
)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Smart Traffic & Urban Incident Classifier API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.state.settings = settings

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    session_cookie="stnlp_oauth_state",
    max_age=600,
    same_site="lax",
    https_only=settings.app_env.lower() not in {"development", "test"},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
)


@app.middleware("http")
async def enforce_cookie_csrf(request, call_next):
    unsafe_methods = {"POST", "PUT", "PATCH", "DELETE"}
    if (
        request.method in unsafe_methods
        and request.url.path != "/api/v1/auth/staff/login"
        and SESSION_COOKIE_NAME in request.cookies
    ):
        origin = request.headers.get("origin")
        if origin and origin not in set(settings.cors_origins):
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid request origin."},
            )

        session_user_id = read_session_token(request.cookies[SESSION_COOKIE_NAME])
        csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
        csrf_header = request.headers.get("X-CSRF-Token")
        if (
            session_user_id is None
            or not csrf_cookie
            or not csrf_header
            or csrf_cookie != csrf_header
            or not validate_csrf_token(session_user_id, csrf_header)
        ):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF validation failed."},
            )

    return await call_next(request)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(citizen_router)
app.include_router(admin_reports_router)
app.include_router(dashboard_router)
app.include_router(attachments_router)
app.include_router(datasets_router)
app.include_router(model_router)
