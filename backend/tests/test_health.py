from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api import health
from app.main import app

client = TestClient(app)


def test_liveness_does_not_depend_on_database() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_returns_ready_when_database_is_available(
    monkeypatch,
) -> None:
    monkeypatch.setattr(health, "check_database_connection", lambda: None)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok"},
    }


def test_readiness_returns_503_when_database_is_unavailable(
    monkeypatch,
) -> None:
    def raise_database_error() -> None:
        raise OperationalError("SELECT 1", {}, RuntimeError("connection refused"))

    monkeypatch.setattr(
        health,
        "check_database_connection",
        raise_database_error,
    )

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "not_ready"
