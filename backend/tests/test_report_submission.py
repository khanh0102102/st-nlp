from __future__ import annotations

import unicodedata
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import app.api.reports as reports_module
from app.api.dependencies import get_current_user, get_db
from app.db.models import Prediction, PreprocessingRun, Report, User
from app.infrastructure.database import engine
from app.main import app


@pytest.fixture
def db_session():
    """Keep endpoint commits inside a rollbackable PostgreSQL outer transaction."""
    with engine.connect() as connection:
        outer_transaction = connection.begin()
        session = Session(
            bind=connection,
            autoflush=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            session.close()
            if outer_transaction.is_active:
                outer_transaction.rollback()


def _citizen(session: Session) -> User:
    user = User(
        email=f"report-ci-{uuid4().hex}@example.test",
        display_name="Report endpoint test",
        role_codes=["CITIZEN"],
    )
    session.add(user)
    session.flush()
    return user


def _client_for(session: Session, user: User):
    previous_overrides = app.dependency_overrides.copy()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: user
    return previous_overrides


def _restore_overrides(previous: dict) -> None:
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def _patch_report_runtime(monkeypatch: pytest.MonkeyPatch, url: str = "") -> None:
    monkeypatch.setattr(
        reports_module,
        "get_settings",
        lambda: type(
            "TestSettings",
            (),
            {
                "ml_service_url": url,
                "ml_internal_token": SecretStr("test-only-token"),
            },
        )(),
    )
    monkeypatch.setattr(reports_module, "_audit", lambda *args, **kwargs: True)


@pytest.mark.parametrize(
    "submitted_text",
    [
        "  Đèn tín hiệu không hoạt động tại ngã tư.  \n",
        "\tĐường bị ngập nước.\r\n  ",
        unicodedata.normalize("NFC", "Cống thoát nước bị nghẹt ở đường Lê Lợi."),
        unicodedata.normalize("NFD", "Đèn đường không sáng vào ban đêm."),
        "  Người dân phản ánh: cây xanh ngã đổ chắn lối đi. \n\n",
    ],
)
def test_report_endpoint_without_ml_service_persists_original_text_and_failure(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    submitted_text: str,
) -> None:
    _patch_report_runtime(monkeypatch, url="")
    user = _citizen(db_session)
    previous = _client_for(db_session, user)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/citizen/reports",
                json={"raw_content": submitted_text},
            )
    finally:
        _restore_overrides(previous)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"data", "meta"}
    assert body["data"]["raw_content"] == submitted_text
    assert set(body["meta"]) == {"prediction", "audit_event_recorded"}
    assert body["meta"]["audit_event_recorded"] is True

    prediction_payload = body["meta"]["prediction"]
    assert {
        "id",
        "inference_status",
        "needs_review",
        "predicted_category",
        "confidence_value",
        "confidence_type",
    } <= set(prediction_payload)
    assert prediction_payload["inference_status"] == "INFERENCE_FAILED"
    assert prediction_payload["predicted_category"] is None
    assert prediction_payload["confidence_value"] is None
    assert prediction_payload["confidence_type"] is None

    report_id = UUID(body["data"]["id"])
    report = db_session.get(Report, report_id)
    assert report is not None
    assert report.raw_content == submitted_text

    predictions = db_session.scalars(
        select(Prediction).where(Prediction.report_id == report_id)
    ).all()
    preprocessing_runs = db_session.scalars(
        select(PreprocessingRun).where(PreprocessingRun.report_id == report_id)
    ).all()
    assert len(predictions) == 1
    assert len(preprocessing_runs) == 1
    assert predictions[0].inference_status == "INFERENCE_FAILED"
    assert predictions[0].predicted_category_id is None
    assert predictions[0].confidence_value is None
    assert predictions[0].confidence_type is None
    assert preprocessing_runs[0].processing_status == "SKIPPED"
    assert preprocessing_runs[0].processed_text is None
    assert db_session.scalar(
        select(Report.id).where(Report.user_id == user.id)
    ) == report_id


def test_report_endpoint_rejects_whitespace_only_without_persisting(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_report_runtime(monkeypatch)
    user = _citizen(db_session)
    previous = _client_for(db_session, user)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/citizen/reports",
                json={"raw_content": " \n\t  "},
            )
    finally:
        _restore_overrides(previous)

    assert response.status_code == 422
    assert db_session.scalar(
        select(Report.id).where(Report.user_id == user.id)
    ) is None
    assert db_session.scalar(
        select(Prediction.id).join(Report).where(Report.user_id == user.id)
    ) is None


def test_configured_but_unavailable_ml_service_does_not_fail_report_creation(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_report_runtime(monkeypatch, url="http://ml-service.test")

    class UnavailableResponse:
        status_code = 503

    class UnavailableClient:
        def __init__(self, timeout: float):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def post(self, *args, **kwargs):
            return UnavailableResponse()

    monkeypatch.setattr(reports_module.httpx, "Client", UnavailableClient)
    user = _citizen(db_session)
    previous = _client_for(db_session, user)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/citizen/reports",
                json={"raw_content": "Biển báo giao thông bị nghiêng."},
            )
    finally:
        _restore_overrides(previous)

    assert response.status_code == 201
    prediction = response.json()["meta"]["prediction"]
    assert prediction["inference_status"] == "INFERENCE_FAILED"
    assert prediction["predicted_category"] is None
    assert prediction["confidence_value"] is None
    report_id = UUID(response.json()["data"]["id"])
    assert db_session.scalar(
        select(Report.id).where(Report.id == report_id)
    ) == report_id
    assert len(
        db_session.scalars(
            select(Prediction).where(Prediction.report_id == report_id)
        ).all()
    ) == 1


def test_malformed_ml_success_response_falls_back_without_fake_prediction(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_report_runtime(monkeypatch, url="http://ml-service.test")

    class MalformedResponse:
        status_code = 200

        def json(self):
            return {"unexpected": "shape"}

    class MalformedClient:
        def __init__(self, timeout: float):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def post(self, *args, **kwargs):
            return MalformedResponse()

    monkeypatch.setattr(reports_module.httpx, "Client", MalformedClient)
    user = _citizen(db_session)
    previous = _client_for(db_session, user)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/citizen/reports",
                json={"raw_content": "Nắp hố ga bị vỡ."},
            )
    finally:
        _restore_overrides(previous)

    assert response.status_code == 201
    prediction = response.json()["meta"]["prediction"]
    assert prediction["inference_status"] == "INFERENCE_FAILED"
    assert prediction["predicted_category"] is None
    assert prediction["confidence_value"] is None
    assert db_session.scalar(
        select(Report.id).where(Report.user_id == user.id)
    ) is not None



def test_database_rejects_mutation_of_original_report_content(
    db_session: Session,
) -> None:
    user = _citizen(db_session)
    original_text = "  Nội dung gốc có dấu tiếng Việt.\n"
    report = Report(user_id=user.id, raw_content=original_text)
    db_session.add(report)
    db_session.flush()

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                update(Report)
                .where(Report.id == report.id)
                .values(raw_content="Nội dung đã bị thay đổi.")
            )

    db_session.refresh(report)
    assert report.raw_content == original_text
