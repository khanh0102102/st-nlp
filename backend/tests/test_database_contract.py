from app.db.base import Base
from app.db import models  # noqa: F401
from app.db.seed import CATEGORIES


EXPECTED_TABLES = {
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


def test_relational_baseline_contains_exactly_twelve_tables() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES
    assert len(Base.metadata.tables) == 12


def test_category_seed_contains_exactly_eleven_unique_codes_and_orders() -> None:
    assert len(CATEGORIES) == 11
    assert len({item[0] for item in CATEGORIES}) == 11
    assert [item[3] for item in CATEGORIES] == list(range(1, 12))
    assert CATEGORIES[-1][0] == "OTHER"
