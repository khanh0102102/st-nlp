from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_roles
from app.core.config import get_settings
from app.db.models import ModelVersion, User
from app.infrastructure.audit import append_audit_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin/models", tags=["model registry"])
MODEL_FAMILIES = {"NB", "SVM", "CNN_1D", "LSTM"}
_MODEL_ACTIVATION_LOCK_NAMESPACE = 1937006963


def _lock_model_activation(session: Session) -> None:
    """Serialize every registry activation/rollback, including the empty-active-set case."""
    session.execute(
        text("SELECT pg_advisory_xact_lock(:namespace, :lock_key)"),
        {"namespace": _MODEL_ACTIVATION_LOCK_NAMESPACE, "lock_key": 1},
    )


class ModelRegister(BaseModel):
    model_family: Literal["NB", "SVM", "CNN_1D", "LSTM"]
    algorithm_name: str = Field(min_length=1, max_length=100)
    version_label: str = Field(min_length=1, max_length=80)
    text_representation: str = Field(min_length=1, max_length=80)
    preprocessing_version: str = Field(min_length=1, max_length=80)
    label_schema_version: str = Field(min_length=1, max_length=40)
    artifact_uri: str = Field(min_length=1, max_length=2000)
    artifact_checksum: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    training_run_id: UUID | None = None
    hyperparameters_json: dict[str, object] | None = None
    metrics_summary_json: dict[str, object] | None = None


def _artifact_path(uri: str) -> Path:
    relative = Path(uri)
    if relative.is_absolute():
        raise HTTPException(status_code=422, detail="Artifact URI must be relative.")
    root = get_settings().model_artifacts_dir.resolve()
    target = (root / relative).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=422, detail="Artifact URI escapes the model storage root.") from None
    if not target.is_file():
        raise HTTPException(status_code=422, detail="Model artifact does not exist in private storage.")
    return target


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _payload(model: ModelVersion) -> dict[str, object]:
    return {
        "id": str(model.id),
        "model_family": model.model_family,
        "algorithm_name": model.algorithm_name,
        "version_label": model.version_label,
        "text_representation": model.text_representation,
        "preprocessing_version": model.preprocessing_version,
        "label_schema_version": model.label_schema_version,
        "training_run_id": str(model.training_run_id) if model.training_run_id else None,
        "artifact_uri": model.artifact_uri,
        "artifact_checksum": model.artifact_checksum,
        "hyperparameters": model.hyperparameters_json,
        "metrics_summary": model.metrics_summary_json,
        "status": model.model_status,
        "registered_by": str(model.registered_by) if model.registered_by else None,
        "approved_by": str(model.approved_by) if model.approved_by else None,
        "approved_at": model.approved_at.isoformat() if model.approved_at else None,
        "activated_at": model.activated_at.isoformat() if model.activated_at else None,
        "retired_at": model.retired_at.isoformat() if model.retired_at else None,
        "created_at": model.created_at.isoformat(),
    }


def _audit(
    request: Request,
    actor: User,
    action: str,
    model: ModelVersion,
    details: dict[str, object] | None = None,
) -> bool:
    try:
        append_audit_event(
            actor_id=actor.id,
            action=action,
            resource_type="model_version",
            resource_id=model.id,
            outcome="SUCCEEDED",
            request_id=getattr(request.state, "request_id", None),
            details=details,
        )
        return True
    except OSError:
        logger.exception("Model registry audit write failed")
        return False


@router.get("")
def list_models(
    model_family: str | None = Query(default=None),
    model_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    query = select(ModelVersion)
    if model_family:
        family = model_family.upper()
        if family not in MODEL_FAMILIES:
            raise HTTPException(status_code=422, detail="Unsupported model family.")
        query = query.where(ModelVersion.model_family == family)
    if model_status:
        query = query.where(ModelVersion.model_status == model_status.upper())

    total = len(session.scalars(query).all())
    rows = session.scalars(
        query.order_by(desc(ModelVersion.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "data": [_payload(row) for row in rows],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def register_model(
    payload: ModelRegister,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    artifact = _artifact_path(payload.artifact_uri)
    checksum = _sha256(artifact)
    if checksum.casefold() != payload.artifact_checksum.casefold():
        raise HTTPException(status_code=422, detail="Artifact checksum does not match the stored file.")

    model = ModelVersion(
        model_family=payload.model_family,
        algorithm_name=payload.algorithm_name.strip(),
        version_label=payload.version_label.strip(),
        text_representation=payload.text_representation.strip(),
        preprocessing_version=payload.preprocessing_version.strip(),
        label_schema_version=payload.label_schema_version.strip(),
        training_run_id=payload.training_run_id,
        artifact_uri=payload.artifact_uri,
        artifact_checksum=checksum,
        hyperparameters_json=payload.hyperparameters_json,
        metrics_summary_json=payload.metrics_summary_json,
        model_status="REGISTERED",
        registered_by=staff.id,
    )
    session.add(model)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(model)
    recorded = _audit(
        request,
        staff,
        "model.registered",
        model,
        {"model_family": model.model_family, "version_label": model.version_label},
    )
    return {"data": _payload(model), "meta": {"audit_event_recorded": recorded}}


@router.get("/{model_id}")
def get_model(
    model_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    model = session.get(ModelVersion, model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model version not found.")
    return {"data": _payload(model)}


@router.post("/{model_id}/approve")
def approve_model(
    model_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    model = session.scalar(
        select(ModelVersion).where(ModelVersion.id == model_id).with_for_update()
    )
    if model is None:
        raise HTTPException(status_code=404, detail="Model version not found.")
    if model.model_status != "EVALUATED":
        raise HTTPException(status_code=409, detail="Only an EVALUATED model can be approved.")
    _artifact_path(model.artifact_uri)
    if _sha256(_artifact_path(model.artifact_uri)) != model.artifact_checksum:
        raise HTTPException(status_code=409, detail="Model artifact checksum validation failed.")

    model.model_status = "APPROVED"
    model.approved_by = staff.id
    model.approved_at = datetime.now(UTC)
    session.commit()
    session.refresh(model)
    recorded = _audit(request, staff, "model.approved", model)
    return {"data": _payload(model), "meta": {"audit_event_recorded": recorded}}


@router.post("/{model_id}/activate")
def activate_model(
    model_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    _lock_model_activation(session)
    model = session.scalar(
        select(ModelVersion).where(ModelVersion.id == model_id).with_for_update()
    )
    if model is None:
        raise HTTPException(status_code=404, detail="Model version not found.")
    if model.model_status != "APPROVED":
        raise HTTPException(status_code=409, detail="Only an APPROVED model can be activated.")
    artifact = _artifact_path(model.artifact_uri)
    if _sha256(artifact) != model.artifact_checksum:
        raise HTTPException(status_code=409, detail="Model artifact checksum validation failed.")

    now = datetime.now(UTC)
    active_models = session.scalars(
        select(ModelVersion)
        .where(ModelVersion.model_status == "ACTIVE")
        .with_for_update()
    ).all()
    for active in active_models:
        active.model_status = "RETIRED"
        active.retired_at = now
    # Flush retirements before setting the new ACTIVE row; the partial
    # unique index is immediate and must not see two ACTIVE rows mid-flush.
    if active_models:
        session.flush()
    model.model_status = "ACTIVE"
    model.activated_at = now
    model.retired_at = None
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Another model activation won the registry concurrency race.",
        ) from exc
    session.refresh(model)
    recorded = _audit(
        request,
        staff,
        "model.activated",
        model,
        {"retired_model_ids": [str(item.id) for item in active_models]},
    )
    return {"data": _payload(model), "meta": {"audit_event_recorded": recorded}}


@router.post("/{model_id}/rollback")
def rollback_model(
    model_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("ADMIN")),
):
    _lock_model_activation(session)
    target = session.scalar(
        select(ModelVersion).where(ModelVersion.id == model_id).with_for_update()
    )
    if target is None:
        raise HTTPException(status_code=404, detail="Model version not found.")
    if target.model_status != "RETIRED" or target.approved_at is None:
        raise HTTPException(status_code=409, detail="Rollback target must be a previously approved RETIRED model.")
    if _sha256(_artifact_path(target.artifact_uri)) != target.artifact_checksum:
        raise HTTPException(status_code=409, detail="Rollback artifact checksum validation failed.")

    now = datetime.now(UTC)
    active_models = session.scalars(
        select(ModelVersion)
        .where(ModelVersion.model_status == "ACTIVE")
        .with_for_update()
    ).all()
    for active in active_models:
        active.model_status = "RETIRED"
        active.retired_at = now
    # Preserve one-ACTIVE invariant with an immediate partial unique index.
    if active_models:
        session.flush()
    target.model_status = "ACTIVE"
    target.activated_at = now
    target.retired_at = None
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Another model activation won the registry concurrency race.",
        ) from exc
    session.refresh(target)
    recorded = _audit(
        request,
        staff,
        "model.rolled_back",
        target,
        {"retired_model_ids": [str(item.id) for item in active_models]},
    )
    return {"data": _payload(target), "meta": {"audit_event_recorded": recorded}}
