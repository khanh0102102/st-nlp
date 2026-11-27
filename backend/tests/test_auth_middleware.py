from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.sessions import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    create_session_token,
)
from app.main import app

client = TestClient(app)


def test_authenticated_mutation_without_csrf_token_is_rejected() -> None:
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token(uuid4()))
    client.cookies.set(CSRF_COOKIE_NAME, "missing-or-invalid")
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF validation failed."
    client.cookies.clear()


def test_staff_login_is_exempt_from_authenticated_csrf_gate() -> None:
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token(uuid4()))
    response = client.post(
        "/api/v1/auth/staff/login",
        json={"email": "unknown@example.com", "password": "not-a-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."
    client.cookies.clear()
