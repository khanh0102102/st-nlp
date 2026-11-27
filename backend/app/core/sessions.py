import secrets
from uuid import UUID

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import get_settings

SESSION_COOKIE_NAME = "stnlp_session"
CSRF_COOKIE_NAME = "stnlp_csrf"
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60
CSRF_MAX_AGE_SECONDS = 60 * 60


def _serializer(salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        get_settings().secret_key.get_secret_value(), salt=salt
    )


def create_session_token(user_id: UUID) -> str:
    return _serializer("stnlp-auth-session").dumps(
        {"sub": str(user_id), "nonce": secrets.token_urlsafe(16)}
    )


def read_session_token(token: str) -> UUID | None:
    try:
        payload = _serializer("stnlp-auth-session").loads(
            token, max_age=SESSION_MAX_AGE_SECONDS
        )
        return UUID(payload["sub"])
    except (BadSignature, SignatureExpired, KeyError, ValueError, TypeError):
        return None


def create_csrf_token(user_id: UUID) -> str:
    return _serializer("stnlp-csrf").dumps(
        {"sub": str(user_id), "nonce": secrets.token_urlsafe(24)}
    )


def validate_csrf_token(user_id: UUID, token: str) -> bool:
    try:
        payload = _serializer("stnlp-csrf").loads(
            token, max_age=CSRF_MAX_AGE_SECONDS
        )
    except (BadSignature, SignatureExpired, KeyError, ValueError, TypeError):
        return False
    return payload.get("sub") == str(user_id)
