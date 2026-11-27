from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_roles
from app.db.models import (
    Dataset,
    DatasetSample,
    IncidentCategory,
    PredictionReview,
    Report,
    User,
)
from app.infrastructure.audit import append_audit_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin/datasets", tags=["dataset management"])
LABEL_STATUSES = {"LABELED", "UNLABELED", "NEEDS_REVIEW", "INSUFFICIENT_INFORMATION"}
SPLITS = {"TRAIN", "VALIDATION", "TEST"}
LABEL_SCHEMA_VERSION = "stnlp-11-categories-v1"


class DatasetCreate(BaseModel):
    dataset_name: str = Field(min_length=1, max_length=150)
    version_label: str = Field(min_length=1, max_length=60)
    label_schema_version: str = Field(default=LABEL_SCHEMA_VERSION, min_length=1, max_length=40)
    split_config_json: dict[str, object] | None = None
    provenance_summary: dict[str, object] | None = None


class DatasetPatch(BaseModel):
    dataset_name: str | None = Field(default=None, min_length=1, max_length=150)
    split_config_json: dict[str, object] | None = None
    provenance_summary: dict[str, object] | None = None


class SampleCreate(BaseModel):
    text_content: str = Field(min_length=1, max_length=20000)
    category_code: str | None = Field(default=None, max_length=50)
    labeling_status: Literal[
        "LABELED", "UNLABELED", "NEEDS_REVIEW", "INSUFFICIENT_INFORMATION"
    ] | None = None
    split: Literal["TRAIN", "VALIDATION", "TEST"] | None = None
    source_type: str = Field(default="MANUAL", min_length=1, max_length=40)
    source_report_id: UUID | None = None
    source_review_id: UUID | None = None
    label_guideline_version: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def validate_source_pair(self):
        if (self.source_report_id is None) != (self.source_review_id is None):
            raise ValueError("source_report_id and source_review_id must be supplied together.")
        return self


class SamplePatch(BaseModel):
    text_content: str | None = Field(default=None, min_length=1, max_length=20000)
    category_code: str | None = Field(default=None, max_length=50)
    labeling_status: Literal[
        "LABELED", "UNLABELED", "NEEDS_REVIEW", "INSUFFICIENT_INFORMATION"
    ] | None = None
    split: Literal["TRAIN", "VALIDATION", "TEST"] | None = None
    label_guideline_version: str | None = Field(default=None, max_length=40)


class NewDatasetVersion(BaseModel):
    version_label: str = Field(min_length=1, max_length=60)


def _audit(request: Request, actor: User, action: str, resource_type: str, resource_id: UUID) -> bool:
    try:
        append_audit_event(
            actor_id=actor.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome="SUCCEEDED",
            request_id=getattr(request.state, "request_id", None),
        )
        return True
    except OSError:
        logger.exception("Dataset audit write failed")
        return False


def _dataset_payload(dataset: Dataset) -> dict[str, object]:
    return {
        "id": str(dataset.id),
        "dataset_name": dataset.dataset_name,
        "version_label": dataset.version_label,
        "parent_dataset_id": str(dataset.parent_dataset_id) if dataset.parent_dataset_id else None,
        "dataset_status": dataset.dataset_status,
        "label_schema_version": dataset.label_schema_version,
        "split_config": dataset.split_config_json,
        "sample_count": dataset.sample_count,
        "class_distribution": dataset.class_distribution_json,
        "validation_report_uri": dataset.validation_report_uri,
        "provenance_summary": dataset.provenance_summary,
        "created_by": str(dataset.created_by),
        "created_at": dataset.created_at.isoformat(),
        "frozen_at": dataset.frozen_at.isoformat() if dataset.frozen_at else None,
    }


def _sample_payload(sample: DatasetSample, category: IncidentCategory | None) -> dict[str, object]:
    return {
        "id": str(sample.id),
        "dataset_id": str(sample.dataset_id),
        "text_content": sample.text_content,
        "category": (
            {
                "id": str(category.id),
                "category_code": category.category_code,
                "category_name": category.category_name,
                "sort_order": category.sort_order,
            }
            if category else None
        ),
        "labeling_status": sample.labeling_status,
        "split": sample.split,
        "source_type": sample.source_type,
        "source_report_id": str(sample.source_report_id) if sample.source_report_id else None,
        "source_review_id": str(sample.source_review_id) if sample.source_review_id else None,
        "text_fingerprint": sample.text_fingerprint,
        "label_guideline_version": sample.label_guideline_version,
        "created_at": sample.created_at.isoformat(),
        "updated_at": sample.updated_at.isoformat(),
    }


def _dataset_for_update(session: Session, dataset_id: UUID) -> Dataset:
    dataset = session.scalar(
        select(Dataset).where(Dataset.id == dataset_id).with_for_update()
    )
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.dataset_status in {"FROZEN", "ARCHIVED"}:
        raise HTTPException(status_code=409, detail="Frozen or archived datasets are read-only.")
    return dataset


def _resolve_label(
    session: Session,
    category_code: str | None,
    labeling_status: str | None,
) -> tuple[IncidentCategory | None, str]:
    category = None
    if category_code:
        category = session.scalar(
            select(IncidentCategory).where(
                IncidentCategory.category_code == category_code,
                IncidentCategory.is_active.is_(True),
            )
        )
        if category is None:
            raise HTTPException(status_code=422, detail="Unknown or inactive category code.")
    state = labeling_status or ("LABELED" if category else "UNLABELED")
    if (category is not None and state != "LABELED") or (
        category is None and state == "LABELED"
    ):
        raise HTTPException(
            status_code=422,
            detail="LABELED samples require a category; non-LABELED samples must not have one.",
        )
    return category, state


def _validate_sample_source(
    session: Session,
    *,
    source_report_id: UUID | None,
    source_review_id: UUID | None,
    category: IncidentCategory | None,
    text_content: str,
) -> None:
    if source_report_id is None and source_review_id is None:
        return
    report = session.get(Report, source_report_id)
    review = session.get(PredictionReview, source_review_id)
    if report is None or review is None or review.report_id != report.id:
        raise HTTPException(status_code=422, detail="Source report and review do not match.")
    if review.selected_category_id != (category.id if category else None):
        raise HTTPException(status_code=422, detail="Sample label must match the selected category in its source review.")
    if text_content != report.raw_content:
        raise HTTPException(status_code=422, detail="Reviewed-report sample text must match the immutable source report.")


def _fingerprint(text_content: str) -> str:
    return hashlib.sha256(text_content.strip().encode("utf-8")).hexdigest()


def _refresh_dataset_stats(session: Session, dataset: Dataset) -> None:
    samples = session.scalars(
        select(DatasetSample).where(DatasetSample.dataset_id == dataset.id)
    ).all()
    dataset.sample_count = len(samples)
    distribution: dict[str, int] = {}
    if samples:
        ids = {item.category_id for item in samples if item.category_id}
        categories = session.scalars(
            select(IncidentCategory).where(IncidentCategory.id.in_(ids))
        ).all() if ids else []
        id_to_code = {item.id: item.category_code for item in categories}
        for sample in samples:
            if sample.category_id and sample.category_id in id_to_code:
                code = id_to_code[sample.category_id]
                distribution[code] = distribution.get(code, 0) + 1
    dataset.class_distribution_json = distribution


def _validation_result(session: Session, dataset: Dataset) -> dict[str, object]:
    samples = session.scalars(
        select(DatasetSample).where(DatasetSample.dataset_id == dataset.id)
    ).all()
    active_categories = session.scalars(
        select(IncidentCategory)
        .where(IncidentCategory.is_active.is_(True))
        .order_by(IncidentCategory.sort_order)
    ).all()
    issues: list[str] = []
    expected_codes = {item.category_code for item in active_categories}

    if len(active_categories) != 11:
        issues.append("The active category catalog must contain exactly 11 categories.")
    if not samples:
        issues.append("Dataset has no samples.")

    labeled = [sample for sample in samples if sample.labeling_status == "LABELED"]
    if not labeled:
        issues.append("Dataset has no labeled samples.")

    by_split = {split: [] for split in SPLITS}
    seen_fingerprints: dict[str, str] = {}
    for sample in labeled:
        if sample.split not in by_split:
            issues.append(f"Sample {sample.id} has no valid data split.")
            continue
        by_split[sample.split].append(sample)
        fingerprint = sample.text_fingerprint or _fingerprint(sample.text_content)
        previous_split = seen_fingerprints.get(fingerprint)
        if previous_split and previous_split != sample.split:
            issues.append("Duplicate text appears in more than one data split.")
        seen_fingerprints[fingerprint] = sample.split

    for split, rows in by_split.items():
        if not rows:
            issues.append(f"Split {split} has no labeled samples.")

    train_codes = {
        next((category.category_code for category in active_categories if category.id == row.category_id), "")
        for row in by_split["TRAIN"]
    }
    missing_train = expected_codes - train_codes
    if missing_train:
        issues.append("TRAIN split is missing categories: " + ", ".join(sorted(missing_train)))

    return {
        "valid": not issues,
        "issues": issues,
        "sample_count": len(samples),
        "labeled_sample_count": len(labeled),
        "split_counts": {split: len(rows) for split, rows in by_split.items()},
        "class_distribution": _class_distribution(session, labeled),
    }


def _class_distribution(
    session: Session,
    samples: list[DatasetSample],
) -> dict[str, int]:
    category_ids = {sample.category_id for sample in samples if sample.category_id}
    categories = session.scalars(
        select(IncidentCategory).where(IncidentCategory.id.in_(category_ids))
    ).all() if category_ids else []
    id_to_code = {item.id: item.category_code for item in categories}
    distribution: dict[str, int] = {}
    for sample in samples:
        if sample.category_id in id_to_code:
            code = id_to_code[sample.category_id]
            distribution[code] = distribution.get(code, 0) + 1
    return distribution


@router.get("")
def list_datasets(
    dataset_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    query = select(Dataset)
    if dataset_status:
        query = query.where(Dataset.dataset_status == dataset_status.upper())
    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = session.scalars(
        query.order_by(desc(Dataset.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "data": [_dataset_payload(row) for row in rows],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_dataset(
    payload: DatasetCreate,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    dataset = Dataset(
        dataset_name=payload.dataset_name.strip(),
        version_label=payload.version_label.strip(),
        dataset_status="DRAFT",
        label_schema_version=payload.label_schema_version,
        split_config_json=payload.split_config_json,
        provenance_summary=payload.provenance_summary,
        sample_count=0,
        class_distribution_json={},
        created_by=staff.id,
    )
    session.add(dataset)
    session.commit()
    session.refresh(dataset)
    recorded = _audit(request, staff, "dataset.created", "dataset", dataset.id)
    return {"data": _dataset_payload(dataset), "meta": {"audit_event_recorded": recorded}}


@router.get("/{dataset_id}")
def get_dataset(
    dataset_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"data": _dataset_payload(dataset)}


@router.patch("/{dataset_id}")
def update_dataset(
    dataset_id: UUID,
    payload: DatasetPatch,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    dataset = _dataset_for_update(session, dataset_id)
    if "dataset_name" in payload.model_fields_set and payload.dataset_name is not None:
        dataset.dataset_name = payload.dataset_name.strip()
    if "split_config_json" in payload.model_fields_set:
        dataset.split_config_json = payload.split_config_json
    if "provenance_summary" in payload.model_fields_set:
        dataset.provenance_summary = payload.provenance_summary
    session.commit()
    session.refresh(dataset)
    recorded = _audit(request, staff, "dataset.updated", "dataset", dataset.id)
    return {"data": _dataset_payload(dataset), "meta": {"audit_event_recorded": recorded}}


@router.get("/{dataset_id}/samples")
def list_dataset_samples(
    dataset_id: UUID,
    split: str | None = Query(default=None),
    labeling_status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    if session.get(Dataset, dataset_id) is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    query = select(DatasetSample).where(DatasetSample.dataset_id == dataset_id)
    if split:
        split = split.upper()
        if split not in SPLITS:
            raise HTTPException(status_code=422, detail="Invalid dataset split.")
        query = query.where(DatasetSample.split == split)
    if labeling_status:
        labeling_status = labeling_status.upper()
        if labeling_status not in LABEL_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid labeling status.")
        query = query.where(DatasetSample.labeling_status == labeling_status)

    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = session.scalars(
        query.order_by(DatasetSample.created_at, DatasetSample.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    categories = {
        item.id: item
        for item in session.scalars(
            select(IncidentCategory).where(
                IncidentCategory.id.in_({row.category_id for row in rows if row.category_id})
            )
        ).all()
    } if any(row.category_id for row in rows) else {}
    return {
        "data": [_sample_payload(row, categories.get(row.category_id)) for row in rows],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("/{dataset_id}/samples", status_code=status.HTTP_201_CREATED)
def create_dataset_sample(
    dataset_id: UUID,
    payload: SampleCreate,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    dataset = _dataset_for_update(session, dataset_id)
    text_content = payload.text_content.strip()
    if not text_content:
        raise HTTPException(status_code=422, detail="Sample text must not be blank.")
    category, label_state = _resolve_label(session, payload.category_code, payload.labeling_status)
    _validate_sample_source(
        session,
        source_report_id=payload.source_report_id,
        source_review_id=payload.source_review_id,
        category=category,
        text_content=text_content,
    )
    fingerprint = _fingerprint(text_content)
    duplicate = session.scalar(
        select(DatasetSample).where(
            DatasetSample.dataset_id == dataset.id,
            DatasetSample.text_fingerprint == fingerprint,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="This text already exists in the dataset.")

    sample = DatasetSample(
        dataset_id=dataset.id,
        text_content=text_content,
        category_id=category.id if category else None,
        labeling_status=label_state,
        split=payload.split,
        source_type=payload.source_type.strip(),
        source_report_id=payload.source_report_id,
        source_review_id=payload.source_review_id,
        text_fingerprint=fingerprint,
        label_guideline_version=payload.label_guideline_version,
    )
    session.add(sample)
    _refresh_dataset_stats(session, dataset)
    session.commit()
    session.refresh(sample)
    recorded = _audit(request, staff, "dataset.sample.created", "dataset", dataset.id)
    return {
        "data": _sample_payload(sample, category),
        "meta": {"audit_event_recorded": recorded},
    }


@router.patch("/samples/{sample_id}")
def update_dataset_sample(
    sample_id: UUID,
    payload: SamplePatch,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    sample = session.scalar(
        select(DatasetSample).where(DatasetSample.id == sample_id).with_for_update()
    )
    if sample is None:
        raise HTTPException(status_code=404, detail="Dataset sample not found.")
    dataset = _dataset_for_update(session, sample.dataset_id)

    text_content = payload.text_content.strip() if payload.text_content is not None else sample.text_content
    category_code = payload.category_code
    if category_code is None and sample.category_id:
        current_category = session.get(IncidentCategory, sample.category_id)
        category_code = current_category.category_code if current_category else None
    elif "category_code" in payload.model_fields_set and payload.category_code is None:
        category_code = None

    label_state_input = payload.labeling_status
    category, label_state = _resolve_label(session, category_code, label_state_input)
    if payload.text_content is not None:
        sample.text_content = text_content
        sample.text_fingerprint = _fingerprint(text_content)
    if "category_code" in payload.model_fields_set or "labeling_status" in payload.model_fields_set:
        sample.category_id = category.id if category else None
        sample.labeling_status = label_state
    if "split" in payload.model_fields_set:
        sample.split = payload.split
    if "label_guideline_version" in payload.model_fields_set:
        sample.label_guideline_version = payload.label_guideline_version

    duplicate = session.scalar(
        select(DatasetSample).where(
            DatasetSample.dataset_id == dataset.id,
            DatasetSample.id != sample.id,
            DatasetSample.text_fingerprint == sample.text_fingerprint,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="This text already exists in the dataset.")
    _validate_sample_source(
        session,
        source_report_id=sample.source_report_id,
        source_review_id=sample.source_review_id,
        category=category,
        text_content=sample.text_content,
    )
    _refresh_dataset_stats(session, dataset)
    session.commit()
    session.refresh(sample)
    recorded = _audit(request, staff, "dataset.sample.updated", "dataset", dataset.id)
    return {
        "data": _sample_payload(sample, category),
        "meta": {"audit_event_recorded": recorded},
    }


@router.delete("/samples/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset_sample(
    sample_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    sample = session.scalar(
        select(DatasetSample).where(DatasetSample.id == sample_id).with_for_update()
    )
    if sample is None:
        raise HTTPException(status_code=404, detail="Dataset sample not found.")
    dataset = _dataset_for_update(session, sample.dataset_id)
    sample_id = sample.id
    session.delete(sample)
    _refresh_dataset_stats(session, dataset)
    session.commit()
    _audit(request, staff, "dataset.sample.deleted", "dataset", dataset.id)


@router.post("/{dataset_id}/validate")
def validate_dataset(
    dataset_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    dataset = _dataset_for_update(session, dataset_id)
    result = _validation_result(session, dataset)
    dataset.sample_count = int(result["sample_count"])
    dataset.class_distribution_json = result["class_distribution"]
    dataset.dataset_status = "READY" if result["valid"] else "DRAFT"
    session.commit()
    recorded = _audit(request, staff, "dataset.validated", "dataset", dataset.id)
    return {
        "data": result,
        "meta": {
            "dataset_status": dataset.dataset_status,
            "audit_event_recorded": recorded,
        },
    }


@router.post("/{dataset_id}/versions", status_code=status.HTTP_201_CREATED)
def create_dataset_version(
    dataset_id: UUID,
    payload: NewDatasetVersion,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    parent = session.scalar(
        select(Dataset).where(Dataset.id == dataset_id).with_for_update()
    )
    if parent is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if parent.dataset_status != "READY":
        raise HTTPException(status_code=409, detail="Only a validated READY dataset can be frozen and versioned.")

    result = _validation_result(session, parent)
    if not result["valid"]:
        raise HTTPException(status_code=409, detail={"message": "Dataset validation failed.", "issues": result["issues"]})

    parent.dataset_status = "FROZEN"
    parent.frozen_at = datetime.now(UTC)
    child = Dataset(
        dataset_name=parent.dataset_name,
        version_label=payload.version_label.strip(),
        parent_dataset_id=parent.id,
        dataset_status="DRAFT",
        label_schema_version=parent.label_schema_version,
        split_config_json=parent.split_config_json,
        sample_count=parent.sample_count,
        class_distribution_json=parent.class_distribution_json,
        provenance_summary={
            "derived_from_dataset_id": str(parent.id),
            "source_provenance": parent.provenance_summary or {},
        },
        created_by=staff.id,
    )
    session.add(child)
    session.flush()

    parent_samples = session.scalars(
        select(DatasetSample).where(DatasetSample.dataset_id == parent.id)
    ).all()
    for sample in parent_samples:
        session.add(
            DatasetSample(
                dataset_id=child.id,
                text_content=sample.text_content,
                category_id=sample.category_id,
                labeling_status=sample.labeling_status,
                split=sample.split,
                source_type=sample.source_type,
                source_report_id=sample.source_report_id,
                source_review_id=sample.source_review_id,
                text_fingerprint=sample.text_fingerprint,
                label_guideline_version=sample.label_guideline_version,
            )
        )

    session.commit()
    session.refresh(parent)
    session.refresh(child)
    recorded = _audit(request, staff, "dataset.version.created", "dataset", child.id)
    return {
        "data": {"frozen_parent": _dataset_payload(parent), "new_version": _dataset_payload(child)},
        "meta": {"audit_event_recorded": recorded},
    }
