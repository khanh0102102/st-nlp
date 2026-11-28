from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import app.api.reports as reports_module
from app.api.dependencies import get_current_user, get_db
from app.db.models import (
    IncidentCategory,
    Prediction,
    PredictionReview,
    PreprocessingRun,
    Report,
    User,
)
from app.infrastructure.database import engine
from app.main import app


@pytest.fixture
def db_session():
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


def _scenario(session: Session):
    citizen = User(
        email=f"review-citizen-{uuid4().hex}@example.test",
        role_codes=["CITIZEN"],
    )
    receiver = User(
        email=f"review-receiver-{uuid4().hex}@example.test",
        role_codes=["RECEIVER"],
    )
    session.add_all([citizen, receiver])
    session.flush()

    categories = session.scalars(
        select(IncidentCategory).order_by(IncidentCategory.sort_order)
    ).all()
    assert len(categories) == 11

    report = Report(user_id=citizen.id, raw_content="Đèn tín hiệu bị hỏng.")
    session.add(report)
    session.flush()
    preprocessing = PreprocessingRun(
        report_id=report.id,
        preprocessing_version="test-skip-v1",
        pipeline_name="test-not-run",
        processing_status="SKIPPED",
    )
    session.add(preprocessing)
    session.flush()
    prediction = Prediction(
        report_id=report.id,
        preprocessing_run_id=preprocessing.id,
        inference_status="INFERENCE_FAILED",
        predicted_category_id=None,
        confidence_value=None,
        confidence_type=None,
    )
    session.add(prediction)
    session.flush()
    return citizen, receiver, report, prediction, categories


def _override_request(session: Session, principal: User) -> dict:
    previous = app.dependency_overrides.copy()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: principal
    return previous


def _restore(previous: dict) -> None:
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def test_receiver_review_updates_final_category_and_history_in_one_transaction(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, receiver, report, prediction, categories = _scenario(db_session)
    monkeypatch.setattr(reports_module, "_audit", lambda *args, **kwargs: True)
    previous = _override_request(db_session, receiver)

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/admin/reports/{report.id}/reviews",
                json={
                    "prediction_id": str(prediction.id),
                    "category_code": categories[7].category_code,
                    "note": "Đã kiểm tra thực tế.",
                },
            )
    finally:
        _restore(previous)

    assert response.status_code == 201
    review_id = response.json()["data"]["id"]
    db_session.refresh(report)
    assert report.final_category_id == categories[7].id

    review = db_session.scalar(
        select(PredictionReview).where(PredictionReview.id == review_id)
    )
    assert review is not None
    assert review.report_id == report.id
    assert review.prediction_id == prediction.id
    assert review.reviewer_id == receiver.id
    assert review.selected_category_id == report.final_category_id
    assert review.action_code == "CORRECTED"


def test_citizen_cannot_call_review_endpoint(
    db_session: Session,
) -> None:
    citizen, _, report, prediction, categories = _scenario(db_session)
    previous = _override_request(db_session, citizen)

    try:
        with TestClient(app) as client:
            response = client.post(
                f"/api/v1/admin/reports/{report.id}/reviews",
                json={
                    "prediction_id": str(prediction.id),
                    "category_code": categories[0].category_code,
                },
            )
    finally:
        _restore(previous)

    assert response.status_code == 403
    assert db_session.scalar(
        select(PredictionReview.id).where(PredictionReview.report_id == report.id)
    ) is None
    db_session.refresh(report)
    assert report.final_category_id is None


def test_database_rejects_citizen_review_insert(
    db_session: Session,
) -> None:
    citizen, _, report, prediction, categories = _scenario(db_session)
    review = PredictionReview(
        report_id=report.id,
        prediction_id=prediction.id,
        reviewer_id=citizen.id,
        selected_category_id=categories[0].id,
        action_code="CORRECTED",
    )

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.add(review)
            db_session.flush()


def test_database_rejects_final_category_change_without_same_transaction_review(
    db_session: Session,
) -> None:
    _, _, report, _, categories = _scenario(db_session)

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                update(Report)
                .where(Report.id == report.id)
                .values(final_category_id=categories[0].id)
            )


def test_database_requires_review_and_final_category_to_commit_together(
    db_session: Session,
) -> None:
    _, receiver, report, prediction, categories = _scenario(db_session)
    review = PredictionReview(
        report_id=report.id,
        prediction_id=prediction.id,
        reviewer_id=receiver.id,
        selected_category_id=categories[0].id,
        action_code="CORRECTED",
    )

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.add(review)
            db_session.flush()
            db_session.execute(
                text(
                    "SET CONSTRAINTS "
                    "trg_prediction_review_requires_final_category IMMEDIATE"
                )
            )



def _insert_review_with_transaction_marker(
    session: Session,
    receiver: User,
    report: Report,
    prediction: Prediction,
    category: IncidentCategory,
) -> PredictionReview:
    review = PredictionReview(
        report_id=report.id,
        prediction_id=prediction.id,
        reviewer_id=receiver.id,
        selected_category_id=category.id,
        action_code="CORRECTED",
        note="Approved review row",
    )
    session.add(review)
    session.flush()
    session.execute(
        text("SELECT set_config('stnlp.current_review_id', :review_id, true)"),
        {"review_id": str(review.id)},
    )
    report.final_category_id = category.id
    session.flush()
    return review


def test_database_requires_matching_transaction_marker_even_with_review_row(
    db_session: Session,
) -> None:
    _, receiver, report, prediction, categories = _scenario(db_session)
    review = PredictionReview(
        report_id=report.id,
        prediction_id=prediction.id,
        reviewer_id=receiver.id,
        selected_category_id=categories[0].id,
        action_code="CORRECTED",
    )

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.add(review)
            db_session.flush()
            db_session.execute(
                update(Report)
                .where(Report.id == report.id)
                .values(final_category_id=categories[0].id)
            )


def test_database_rejects_update_of_review_history(
    db_session: Session,
) -> None:
    _, receiver, report, prediction, categories = _scenario(db_session)
    review = _insert_review_with_transaction_marker(
        db_session, receiver, report, prediction, categories[0]
    )

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                update(PredictionReview)
                .where(PredictionReview.id == review.id)
                .values(note="attempted mutation")
            )


def test_database_rejects_delete_of_review_history(
    db_session: Session,
) -> None:
    _, receiver, report, prediction, categories = _scenario(db_session)
    review = _insert_review_with_transaction_marker(
        db_session, receiver, report, prediction, categories[0]
    )

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                delete(PredictionReview).where(PredictionReview.id == review.id)
            )

    assert db_session.scalar(
        select(PredictionReview.id).where(PredictionReview.id == review.id)
    ) == review.id
