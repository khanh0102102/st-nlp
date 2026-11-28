from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.seed import CATEGORIES
from app.infrastructure.database import engine


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


def test_postgresql_contains_exactly_the_twelve_business_tables(
    db_session: Session,
) -> None:
    table_names = set(
        db_session.scalars(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = current_schema() "
                "AND tablename <> 'alembic_version'"
            )
        ).all()
    )
    assert table_names == {
        "users",
        "incident_categories",
        "reports",
        "report_attachments",
        "preprocessing_runs",
        "model_versions",
        "predictions",
        "prediction_reviews",
        "datasets",
        "dataset_samples",
        "training_runs",
        "training_metrics",
    }
    assert len(table_names) == 12


def test_postgresql_seed_has_exactly_eleven_categories(
    db_session: Session,
) -> None:
    rows = db_session.execute(
        text(
            "SELECT category_code, sort_order FROM incident_categories "
            "WHERE is_active IS TRUE ORDER BY sort_order"
        )
    ).all()
    assert len(rows) == 11
    assert [row.category_code for row in rows] == [row[0] for row in CATEGORIES]
    assert [row.sort_order for row in rows] == list(range(1, 12))
