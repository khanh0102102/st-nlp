from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.ml.training as training_module
from app.db.models import (
    Dataset,
    DatasetSample,
    IncidentCategory,
    ModelVersion,
    TrainingMetric,
    TrainingRun,
    User,
)
from app.infrastructure.database import engine
from app.ml.classical import load_classical_artifact, predict_classical


@pytest.fixture
def db_session():
    """Use a savepoint-backed session so service commits remain rollbackable."""
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


def _create_admin(session: Session) -> User:
    user = User(
        email=f"ml-ci-{uuid4().hex}@example.test",
        display_name="ML integration test",
        role_codes=["ADMIN"],
    )
    session.add(user)
    session.flush()
    return user


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _create_dataset(
    session: Session,
    *,
    user: User,
    include_all_splits: bool = True,
) -> tuple[Dataset, list[IncidentCategory]]:
    categories = session.scalars(
        select(IncidentCategory)
        .where(IncidentCategory.is_active.is_(True))
        .order_by(IncidentCategory.sort_order)
    ).all()
    assert len(categories) == 11

    dataset = Dataset(
        dataset_name=f"synthetic-ml-ci-{uuid4().hex[:10]}",
        version_label="v1",
        dataset_status="DRAFT",
        label_schema_version="stnlp-11-categories-v1",
        split_config_json={"TRAIN": 0.5, "VALIDATION": 0.25, "TEST": 0.25},
        sample_count=0,
        class_distribution_json={},
        provenance_summary={"purpose": "synthetic CI mechanics test; not model evaluation"},
        created_by=user.id,
    )
    session.add(dataset)
    session.flush()

    samples: list[DatasetSample] = []
    splits = ("TRAIN", "VALIDATION", "TEST") if include_all_splits else ("TRAIN",)
    for category in categories:
        for split in splits:
            sample_repeats = 2 if split == "TRAIN" else 1
            for repeat in range(sample_repeats):
                text = (
                    f"{category.category_name}. "
                    f"Danh mục {category.category_code}. "
                    f"Mẫu {split.lower()} số {repeat} cho kiểm thử cơ chế."
                )
                samples.append(
                    DatasetSample(
                        dataset_id=dataset.id,
                        text_content=text,
                        category_id=category.id,
                        labeling_status="LABELED",
                        split=split,
                        source_type="SYNTHETIC_CI",
                        text_fingerprint=_fingerprint(text),
                        label_guideline_version="ci-test-v1",
                    )
                )

    session.add_all(samples)
    session.flush()

    distribution = {category.category_code: 0 for category in categories}
    for sample in samples:
        category = next(item for item in categories if item.id == sample.category_id)
        distribution[category.category_code] += 1

    dataset.sample_count = len(samples)
    dataset.class_distribution_json = distribution
    dataset.dataset_status = "FROZEN"
    dataset.frozen_at = datetime.now(UTC)
    session.flush()
    return dataset, categories


@pytest.mark.parametrize(
    ("model_family", "expected_confidence_type"),
    [
        ("NB", "MODEL_PROBABILITY_UNCALIBRATED"),
        ("SVM", "RAW_DECISION_SCORE"),
    ],
)
def test_frozen_dataset_training_persists_run_metrics_registry_and_artifact(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    model_family: str,
    expected_confidence_type: str,
) -> None:
    user = _create_admin(db_session)
    dataset, categories = _create_dataset(db_session, user=user)
    artifacts_dir = tmp_path / "model-artifacts"
    monkeypatch.setattr(
        training_module,
        "get_settings",
        lambda: SimpleNamespace(model_artifacts_dir=artifacts_dir),
    )

    model_version = training_module.train_registered_model(
        session=db_session,
        dataset_id=dataset.id,
        model_family=model_family,
        created_by=user.id,
        random_seed=19,
    )

    assert model_version.model_family == model_family
    assert model_version.model_status == "EVALUATED"
    assert model_version.training_run_id is not None
    assert model_version.registered_by == user.id
    assert model_version.label_schema_version == "stnlp-11-categories-v1"

    run = db_session.get(TrainingRun, model_version.training_run_id)
    assert run is not None
    assert run.dataset_id == dataset.id
    assert run.run_status == "SUCCEEDED"
    assert run.finished_at is not None
    assert run.duration_ms is not None and run.duration_ms >= 0
    assert run.failure_summary is None
    assert run.output_artifact_uri == model_version.artifact_uri

    artifact_path = artifacts_dir / model_version.artifact_uri
    assert artifact_path.is_file()
    artifact_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    assert artifact_sha == model_version.artifact_checksum

    loaded_model, metadata = load_classical_artifact(artifact_path)
    assert metadata["model_family"] == model_family
    assert metadata["confidence_type"] == expected_confidence_type
    assert set(metadata["class_codes"]) == {category.category_code for category in categories}

    sample_text = (
        f"{categories[0].category_name}. Danh mục {categories[0].category_code}."
    )
    prediction = predict_classical(loaded_model, metadata, sample_text)
    assert prediction["category_code"] in metadata["class_codes"]
    assert prediction["confidence_type"] == expected_confidence_type
    assert prediction["preprocessing_version"] == model_version.preprocessing_version

    metrics = db_session.scalars(
        select(TrainingMetric).where(
            TrainingMetric.training_run_id == run.id
        )
    ).all()
    assert len(metrics) == 120
    assert {metric.data_split for metric in metrics} == {
        "TRAIN",
        "VALIDATION",
        "TEST",
    }
    assert all(metric.support_count is not None for metric in metrics)

    accuracy_by_split = {
        metric.data_split: metric
        for metric in metrics
        if metric.metric_name == "accuracy"
    }
    assert set(accuracy_by_split) == {"TRAIN", "VALIDATION", "TEST"}
    for accuracy_metric in accuracy_by_split.values():
        assert accuracy_metric.metric_details_json is not None
        matrix = accuracy_metric.metric_details_json["confusion_matrix"]
        assert len(matrix) == 11
        assert all(len(row) == 11 for row in matrix)

    assert set(model_version.metrics_summary_json) == {
        "TRAIN",
        "VALIDATION",
        "TEST",
    }
    assert all(
        "f1_macro" in split_summary
        for split_summary in model_version.metrics_summary_json.values()
    )


def test_training_rejects_dataset_before_freeze_without_creating_run(
    db_session: Session,
) -> None:
    user = _create_admin(db_session)
    dataset = Dataset(
        dataset_name=f"draft-dataset-{uuid4().hex[:10]}",
        version_label="v1",
        dataset_status="DRAFT",
        label_schema_version="stnlp-11-categories-v1",
        sample_count=0,
        created_by=user.id,
    )
    db_session.add(dataset)
    db_session.flush()

    with pytest.raises(ValueError, match="FROZEN"):
        training_module.train_registered_model(
            session=db_session,
            dataset_id=dataset.id,
            model_family="NB",
            created_by=user.id,
        )

    runs = db_session.scalars(
        select(TrainingRun).where(TrainingRun.dataset_id == dataset.id)
    ).all()
    assert runs == []


def test_training_rejects_identical_text_fingerprint_across_splits(
    db_session: Session,
) -> None:
    user = _create_admin(db_session)
    categories = db_session.scalars(
        select(IncidentCategory)
        .where(IncidentCategory.is_active.is_(True))
        .order_by(IncidentCategory.sort_order)
    ).all()
    dataset = Dataset(
        dataset_name=f"leakage-dataset-{uuid4().hex[:10]}",
        version_label="v1",
        dataset_status="DRAFT",
        label_schema_version="stnlp-11-categories-v1",
        sample_count=0,
        created_by=user.id,
    )
    db_session.add(dataset)
    db_session.flush()

    duplicate_text = "Cống thoát nước bị nghẹt tại tuyến đường kiểm thử."
    fingerprint = _fingerprint(duplicate_text)
    db_session.add_all(
        [
            DatasetSample(
                dataset_id=dataset.id,
                text_content=duplicate_text,
                category_id=categories[0].id,
                labeling_status="LABELED",
                split="TRAIN",
                source_type="SYNTHETIC_CI",
                text_fingerprint=fingerprint,
            ),
            DatasetSample(
                dataset_id=dataset.id,
                text_content=duplicate_text,
                category_id=categories[0].id,
                labeling_status="LABELED",
                split="VALIDATION",
                source_type="SYNTHETIC_CI",
                text_fingerprint=fingerprint,
            ),
        ]
    )
    db_session.flush()
    dataset.sample_count = 2
    dataset.dataset_status = "FROZEN"
    dataset.frozen_at = datetime.now(UTC)
    db_session.flush()

    with pytest.raises(ValueError, match="multiple dataset splits"):
        training_module._load_training_data(db_session, dataset.id)

    runs = db_session.scalars(
        select(TrainingRun).where(TrainingRun.dataset_id == dataset.id)
    ).all()
    assert runs == []
