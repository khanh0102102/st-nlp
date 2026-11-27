from __future__ import annotations

import hashlib
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import joblib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    Dataset,
    DatasetSample,
    IncidentCategory,
    ModelVersion,
    TrainingMetric,
    TrainingRun,
)
from app.ml.classical import fit_classical
from app.ml.metrics import evaluate_predictions, flatten_metrics
from app.ml.preprocessing import PREPROCESSING_VERSION

SUPPORTED_FAMILIES = {"NB", "SVM", "CNN_1D", "LSTM"}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_training_data(session: Session, dataset_id: UUID):
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise ValueError("Dataset does not exist.")
    if dataset.dataset_status != "FROZEN":
        raise ValueError("Training requires a FROZEN dataset version.")

    rows = session.scalars(
        select(DatasetSample)
        .where(
            DatasetSample.dataset_id == dataset_id,
            DatasetSample.labeling_status == "LABELED",
        )
        .order_by(DatasetSample.created_at, DatasetSample.id)
    ).all()
    if not rows:
        raise ValueError("Frozen dataset contains no labeled samples.")

    category_rows = session.scalars(
        select(IncidentCategory).where(IncidentCategory.is_active.is_(True))
    ).all()
    id_to_code = {row.id: row.category_code for row in category_rows}
    class_codes = sorted(id_to_code.values())
    if len(class_codes) != 11:
        raise ValueError("Exactly 11 active categories must exist before training.")

    by_split: dict[str, list[DatasetSample]] = {
        "TRAIN": [],
        "VALIDATION": [],
        "TEST": [],
    }
    fingerprints: dict[str, str] = {}
    for row in rows:
        if row.category_id is None or row.category_id not in id_to_code:
            raise ValueError(f"Labeled sample {row.id} has an invalid category.")
        if row.split not in by_split:
            raise ValueError(f"Sample {row.id} has no valid TRAIN/VALIDATION/TEST split.")
        fingerprint = row.text_fingerprint or hashlib.sha256(
            row.text_content.encode("utf-8")
        ).hexdigest()
        previous_split = fingerprints.get(fingerprint)
        if previous_split and previous_split != row.split:
            raise ValueError(
                "Identical text fingerprint appears in multiple dataset splits."
            )
        fingerprints[fingerprint] = row.split
        by_split[row.split].append(row)

    for split, split_rows in by_split.items():
        if not split_rows:
            raise ValueError(f"Dataset split {split} is empty.")

    train_codes = {id_to_code[row.category_id] for row in by_split["TRAIN"]}
    missing_train = set(class_codes) - train_codes
    if missing_train:
        raise ValueError(
            "TRAIN split must contain all 11 categories; missing: "
            + ", ".join(sorted(missing_train))
        )

    payload = {}
    for split, split_rows in by_split.items():
        payload[split] = {
            "texts": [row.text_content for row in split_rows],
            "labels": [id_to_code[row.category_id] for row in split_rows],
        }
    return dataset, payload, class_codes, category_rows


def train_registered_model(
    *,
    session: Session,
    dataset_id: UUID,
    model_family: str,
    created_by: UUID,
    random_seed: int = 42,
    epochs: int = 15,
) -> ModelVersion:
    family = model_family.upper()
    if family not in SUPPORTED_FAMILIES:
        raise ValueError("model_family must be NB, SVM, CNN_1D or LSTM.")

    dataset, splits, class_codes, categories = _load_training_data(
        session, dataset_id
    )
    started = datetime.now(UTC)
    run = TrainingRun(
        dataset_id=dataset_id,
        model_family=family,
        algorithm_name={
            "NB": "MultinomialNB",
            "SVM": "LinearSVC",
            "CNN_1D": "TextCNN1D",
            "LSTM": "BidirectionalLSTM",
        }[family],
        text_representation=(
            "TFIDF_WORD_NGRAM_1_2" if family in {"NB", "SVM"} else "TOKEN_IDS_VOCAB"
        ),
        hyperparameters_json={
            "random_seed": random_seed,
            "epochs": epochs if family in {"CNN_1D", "LSTM"} else None,
            "class_count": len(class_codes),
            "splits": {key: len(value["labels"]) for key, value in splits.items()},
        },
        preprocessing_version=PREPROCESSING_VERSION,
        random_seed=random_seed,
        code_version=os.getenv("GIT_COMMIT_SHA"),
        environment_version=f"python-{platform.python_version()}",
        run_status="RUNNING",
        started_at=started,
        created_by=created_by,
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    settings = get_settings()
    version_label = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    suffix = ".joblib" if family in {"NB", "SVM"} else ".pt"
    relative_path = Path("models") / family.lower() / version_label / ("model" + suffix)
    artifact_path = settings.model_artifacts_dir / relative_path
    started_clock = time.monotonic()

    try:
        if family in {"NB", "SVM"}:
            model, metadata = fit_classical(
                family,
                splits["TRAIN"]["texts"],
                splits["TRAIN"]["labels"],
                random_seed,
            )
            metrics = {
                split: evaluate_predictions(
                    values["labels"],
                    model.predict(values["texts"]).tolist(),
                    class_codes,
                )
                for split, values in splits.items()
            }
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(
                {"pipeline": model, "metadata": metadata},
                artifact_path,
                compress=3,
            )
            hyperparameters = {
                "tfidf": metadata["vectorizer"],
                "classifier": metadata["hyperparameters"],
                "confidence_type": metadata["confidence_type"],
            }
        else:
            try:
                from app.ml.neural import train_neural
            except ImportError as exc:
                raise RuntimeError(
                    "CNN_1D/LSTM training requires the optional neural dependencies "
                    "listed in backend/requirements-neural.txt."
                ) from exc

            metadata, metrics = train_neural(
                model_family=family,
                train_texts=splits["TRAIN"]["texts"],
                train_labels=splits["TRAIN"]["labels"],
                validation_texts=splits["VALIDATION"]["texts"],
                validation_labels=splits["VALIDATION"]["labels"],
                test_texts=splits["TEST"]["texts"],
                test_labels=splits["TEST"]["labels"],
                class_codes=class_codes,
                output_path=artifact_path,
                random_seed=random_seed,
                epochs=epochs,
            )
            hyperparameters = {
                "max_epochs": epochs,
                "best_epoch": metadata["best_epoch"],
                "seed": random_seed,
                "confidence_type": metadata["confidence_type"],
            }

        checksum = _sha256_file(artifact_path)
        elapsed_ms = int((time.monotonic() - started_clock) * 1000)
        metric_rows = flatten_metrics(metrics)
        code_to_id = {row.category_code: row.id for row in categories}
        for item in metric_rows:
            category_id = (
                code_to_id[item["category_code"]]
                if item["category_code"]
                else None
            )
            session.add(
                TrainingMetric(
                    training_run_id=run.id,
                    metric_name=item["metric_name"],
                    metric_value=item["metric_value"],
                    data_split=item["data_split"],
                    averaging=item["averaging"],
                    category_id=category_id,
                    support_count=item["support_count"],
                    metric_details_json=item.get("metric_details_json"),
                )
            )

        run.run_status = "SUCCEEDED"
        run.finished_at = datetime.now(UTC)
        run.duration_ms = elapsed_ms
        run.output_artifact_uri = relative_path.as_posix()
        run.hyperparameters_json = {
            **(run.hyperparameters_json or {}),
            **hyperparameters,
        }
        summary = {
            split: {
                "accuracy": values["accuracy"],
                "precision_macro": values["precision_macro"],
                "recall_macro": values["recall_macro"],
                "f1_macro": values["f1_macro"],
                "f1_weighted": values["f1_weighted"],
                "support": values["support"],
            }
            for split, values in metrics.items()
        }
        model_version = ModelVersion(
            model_family=family,
            algorithm_name=run.algorithm_name,
            version_label=version_label,
            text_representation=run.text_representation,
            preprocessing_version=PREPROCESSING_VERSION,
            label_schema_version="stnlp-11-categories-v1",
            training_run_id=run.id,
            artifact_uri=relative_path.as_posix(),
            artifact_checksum=checksum,
            hyperparameters_json=run.hyperparameters_json,
            metrics_summary_json=summary,
            model_status="EVALUATED",
            registered_by=created_by,
        )
        session.add(model_version)
        session.commit()
        session.refresh(model_version)
        return model_version
    except Exception as exc:
        session.rollback()
        failed_run = session.get(TrainingRun, run.id)
        if failed_run is not None:
            failed_run.run_status = "FAILED"
            failed_run.finished_at = datetime.now(UTC)
            failed_run.duration_ms = int((time.monotonic() - started_clock) * 1000)
            failed_run.failure_summary = f"{type(exc).__name__}: {exc}"[:2000]
            session.commit()
        raise
