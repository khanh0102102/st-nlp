from fastapi.testclient import TestClient

from app.db.seed import CATEGORIES
from app.main import app

client = TestClient(app)


def test_public_category_catalog_returns_exactly_eleven_in_order() -> None:
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert len(payload) == 11
    assert [row["category_code"] for row in payload] == [row[0] for row in CATEGORIES]
    assert [row["sort_order"] for row in payload] == list(range(1, 12))


def test_citizen_report_list_requires_authentication() -> None:
    response = client.get("/api/v1/citizen/reports")
    assert response.status_code == 401


def test_admin_report_list_requires_staff_authentication() -> None:
    response = client.get("/api/v1/admin/reports")
    assert response.status_code == 401
