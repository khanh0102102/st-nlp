from __future__ import annotations

import hashlib
import logging
import os
import httpx
import re
import uuid
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_roles
from app.core.config import get_settings
from app.db.models import (
    IncidentCategory, ModelVersion, Prediction, PredictionReview,
    PreprocessingRun, Report, ReportAttachment, User,
)
from app.infrastructure.audit import append_audit_event, read_resource_audit_events

citizen_router = APIRouter(prefix="/api/v1", tags=["citizen"])
admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
catalog_router = APIRouter(prefix="/api/v1", tags=["catalog"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": (".jpg", ".jpeg"),
    "image/png": (".png",),
    "image/webp": (".webp",),
}
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_FILES_PER_REPORT = 5
MAX_PAGE_SIZE = 100
VALID_WORKFLOW = {
    "SUBMITTED": {"UNDER_REVIEW", "REJECTED"},
    "UNDER_REVIEW": {"IN_PROGRESS", "REJECTED"},
    "IN_PROGRESS": {"RESOLVED", "REJECTED"},
    "RESOLVED": {"CLOSED"},
    "REJECTED": {"CLOSED"},
    "CLOSED": set(),
}


class ReportCreate(BaseModel):
    raw_content: str = Field(min_length=1, max_length=20000)
    address: str | None = Field(default=None, max_length=2000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ProfilePatch(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=150)


class ReviewCreate(BaseModel):
    category_code: str = Field(min_length=1, max_length=50)
    prediction_id: UUID | None = None
    note: str | None = Field(default=None, max_length=2000)


class StatusPatch(BaseModel):
    status: str = Field(min_length=1, max_length=40)


def _category_payload(category: IncidentCategory | None):
    if category is None:
        return None
    return {
        "id": str(category.id),
        "category_code": category.category_code,
        "category_name": category.category_name,
        "sort_order": category.sort_order,
    }


def _report_payload(
    report: Report,
    category: IncidentCategory | None = None,
    *,
    include_owner: bool = False,
):
    data = {
        "id": str(report.id),
        "raw_content": report.raw_content,
        "address": report.address,
        "latitude": float(report.latitude) if report.latitude is not None else None,
        "longitude": float(report.longitude) if report.longitude is not None else None,
        "status": report.status,
        "final_category": _category_payload(category),
        "submitted_at": report.submitted_at.isoformat(),
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat(),
    }
    if include_owner:
        data["user_id"] = str(report.user_id)
    return data


def _owned_report(session: Session, report_id: UUID, user_id: UUID) -> Report:
    report = session.scalar(
        select(Report).where(Report.id == report_id, Report.user_id == user_id)
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


def _verified_image_mime(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def _safe_filename(filename: str | None, mime_type: str) -> str:
    allowed = ALLOWED_IMAGE_TYPES[mime_type]
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename or "upload").name)[:255]
    if Path(safe).suffix.lower() not in allowed:
        return f"attachment{allowed[0]}"
    return safe or f"attachment{allowed[0]}"


def _audit(
    request: Request,
    *,
    actor_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: UUID,
    details: dict | None = None,
) -> bool:
    try:
        append_audit_event(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome="SUCCEEDED",
            request_id=getattr(request.state, "request_id", None),
            details=details,
        )
        return True
    except OSError:
        logging.getLogger(__name__).exception("Local audit sink write failed")
        return False


@catalog_router.get("/categories")
def list_categories(session: Session = Depends(get_db)):
    rows = session.scalars(
        select(IncidentCategory)
        .where(IncidentCategory.is_active.is_(True))
        .order_by(IncidentCategory.sort_order)
    ).all()
    return {"data": [_category_payload(row) for row in rows]}


@citizen_router.get("/citizen/profile")
def get_profile(user: User = Depends(get_current_user)):
    if "CITIZEN" not in set(user.role_codes or []):
        raise HTTPException(status_code=403, detail="Citizen access required.")
    return {"data": {
        "id": str(user.id), "email": user.email,
        "display_name": user.display_name, "avatar_url": user.avatar_url,
    }}


@citizen_router.patch("/citizen/profile")
def update_profile(
    payload: ProfilePatch,
    request: Request,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if "CITIZEN" not in set(user.role_codes or []):
        raise HTTPException(status_code=403, detail="Citizen access required.")
    if "display_name" in payload.model_fields_set:
        user.display_name = payload.display_name.strip() if payload.display_name else None
    session.commit()
    session.refresh(user)
    recorded = _audit(
        request, actor_id=user.id, action="citizen.profile.updated",
        resource_type="user", resource_id=user.id,
        details={"changed_fields": sorted(payload.model_fields_set)},
    )
    return {
        "data": {
            "id": str(user.id), "email": user.email,
            "display_name": user.display_name, "avatar_url": user.avatar_url,
        },
        "meta": {"audit_event_recorded": recorded},
    }


@citizen_router.post("/citizen/reports", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    request: Request,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if "CITIZEN" not in set(user.role_codes or []):
        raise HTTPException(status_code=403, detail="Citizen access required.")
    if (payload.latitude is None) != (payload.longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude and longitude must be provided together.",
        )
    # Validate whitespace without altering the citizen's submitted text.
    raw_content = payload.raw_content
    if not raw_content.strip():
        raise HTTPException(status_code=422, detail="Report content is required.")

    report = Report(
        user_id=user.id, raw_content=raw_content,
        address=payload.address.strip() if payload.address else None,
        latitude=payload.latitude, longitude=payload.longitude,
        status="SUBMITTED",
    )
    session.add(report)
    session.flush()

    # Until a model is registered, save the report and an explicit unavailable
    # inference record. Do not invent an AI label or substitute OTHER.
    preprocessing = PreprocessingRun(
        report_id=report.id,
        preprocessing_version="nlp-not-configured",
        pipeline_name="not-run",
        normalization_config_json={"status": "not_configured"},
        processing_status="SKIPPED",
        error_code="NLP_PIPELINE_NOT_READY",
    )
    session.add(preprocessing)
    session.flush()
    prediction = Prediction(
        report_id=report.id,
        preprocessing_run_id=preprocessing.id,
        model_version_id=None,
        predicted_category_id=None,
        confidence_value=None,
        confidence_type=None,
        needs_review=True,
        inference_status="INFERENCE_FAILED",
        error_code="NO_ACTIVE_MODEL",
    )
    session.add(prediction)
    session.commit()
    session.refresh(report)

    prediction_payload = {
        "id": str(prediction.id),
        "inference_status": prediction.inference_status,
        "needs_review": True,
        "predicted_category": None,
        "confidence_value": None,
        "confidence_type": None,
    }
    settings = get_settings()
    if settings.ml_service_url.strip():
        try:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(
                    settings.ml_service_url.rstrip("/") + "/internal/v1/predict",
                    headers={
                        "Authorization": "Bearer "
                        + settings.ml_internal_token.get_secret_value()
                    },
                    json={"report_id": str(report.id)},
                )
            if response.status_code == 200:
                body = response.json()
                candidate = body.get("data") if isinstance(body, dict) else None
                allowed_statuses = {
                    "PENDING", "SUCCEEDED", "INSUFFICIENT_INFORMATION",
                    "INVALID_INPUT", "INFERENCE_FAILED",
                }
                if (
                    not isinstance(candidate, dict)
                    or candidate.get("inference_status") not in allowed_statuses
                    or (
                        candidate.get("inference_status") == "SUCCEEDED"
                        and candidate.get("predicted_category") is None
                    )
                    or (
                        candidate.get("inference_status") != "SUCCEEDED"
                        and candidate.get("predicted_category") is not None
                    )
                    or (
                        candidate.get("confidence_value") is not None
                        and candidate.get("confidence_type") is None
                    )
                ):
                    raise ValueError("ML service response does not match the prediction contract.")
                prediction_payload = candidate
            elif response.status_code != 409:
                logging.getLogger(__name__).warning(
                    "ML service returned HTTP %s for report %s",
                    response.status_code,
                    report.id,
                )
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
            logging.getLogger(__name__).info(
                "ML service unavailable or returned an invalid response (%s); report %s remains saved without a successful inference.",
                type(exc).__name__,
                report.id,
            )

    # Audit every accepted report, including the normal no-ML-service path.
    recorded = _audit(
        request,
        actor_id=user.id,
        action="report.submitted",
        resource_type="report",
        resource_id=report.id,
        details={
            "status": report.status,
            "inference_status": prediction_payload["inference_status"],
            "attachment_count": 0,
        },
    )
    return {
        "data": _report_payload(report),
        "meta": {
            "prediction": {
                **prediction_payload,
            },
            "audit_event_recorded": recorded,
        },
    }


@citizen_router.get("/citizen/reports")
def list_my_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=MAX_PAGE_SIZE),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = select(Report).where(Report.user_id == user.id)
    total = session.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = session.scalars(
        base.order_by(desc(Report.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {
        "data": [_report_payload(row) for row in rows],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@citizen_router.get("/citizen/reports/{report_id}")
def get_my_report(
    report_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = _owned_report(session, report_id, user.id)
    category = (
        session.get(IncidentCategory, report.final_category_id)
        if report.final_category_id else None
    )
    attachments = session.scalars(
        select(ReportAttachment).where(
            ReportAttachment.report_id == report.id,
            ReportAttachment.upload_status == "READY",
        ).order_by(ReportAttachment.created_at)
    ).all()
    return {
        "data": _report_payload(report, category),
        "attachments": [
            {
                "id": str(item.id), "filename": item.original_filename,
                "mime_type": item.verified_mime_type,
                "size_bytes": item.file_size_bytes,
                "created_at": item.created_at.isoformat(),
            } for item in attachments
        ],
    }


@citizen_router.get("/citizen/reports/{report_id}/prediction")
def get_my_prediction(
    report_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_report(session, report_id, user.id)
    prediction = session.scalar(
        select(Prediction).where(Prediction.report_id == report_id)
        .order_by(desc(Prediction.created_at)).limit(1)
    )
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found.")
    category = (
        session.get(IncidentCategory, prediction.predicted_category_id)
        if prediction.predicted_category_id else None
    )
    model = (
        session.get(ModelVersion, prediction.model_version_id)
        if prediction.model_version_id else None
    )
    return {"data": {
        "id": str(prediction.id),
        "predicted_category": _category_payload(category),
        "confidence_value": (
            float(prediction.confidence_value)
            if prediction.confidence_value is not None else None
        ),
        "confidence_type": prediction.confidence_type,
        "model_version": model.version_label if model else None,
        "inference_status": prediction.inference_status,
        "needs_review": prediction.needs_review,
    }}


@citizen_router.get("/citizen/reports/{report_id}/history")
def get_my_report_history(
    report_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_report(session, report_id, user.id)
    events = read_resource_audit_events(resource_type="report", resource_id=report_id)
    public_actions = {
        "report.submitted", "report.status.changed", "report.reviewed",
    }
    return {"data": [
        {
            "action": event["action"],
            "timestamp": event["timestamp"],
            "status": event.get("details", {}).get("to_status"),
        }
        for event in events if event.get("action") in public_actions
    ]}


async def _store_attachment(
    report_id: UUID,
    request: Request,
    file: UploadFile,
    session: Session,
    user: User,
):
    report = _owned_report(session, report_id, user.id)
    count = session.scalar(
        select(func.count()).select_from(ReportAttachment)
        .where(ReportAttachment.report_id == report.id)
    ) or 0
    if count >= MAX_FILES_PER_REPORT:
        raise HTTPException(status_code=422, detail="Maximum 5 attachments per report.")

    content = await file.read(MAX_FILE_BYTES + 1)
    if not content:
        raise HTTPException(status_code=422, detail="Empty files are not allowed.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Maximum file size is 10 MiB.")
    mime_type = _verified_image_mime(content)
    if mime_type is None:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG, PNG and WebP images are accepted.",
        )

    safe_name = _safe_filename(file.filename, mime_type)
    storage_dir = get_settings().uploads_dir.resolve()
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = uuid.uuid4().hex
    target = (storage_dir / storage_key).resolve()
    if target.parent != storage_dir:
        raise HTTPException(status_code=400, detail="Invalid storage path.")

    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(content)
    except OSError:
        raise HTTPException(
            status_code=500, detail="Attachment could not be stored."
        ) from None

    attachment = ReportAttachment(
        report_id=report.id, uploaded_by=user.id,
        storage_key=storage_key, original_filename=safe_name,
        verified_mime_type=mime_type, file_size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        upload_status="READY",
    )
    try:
        session.add(attachment)
        session.commit()
        session.refresh(attachment)
    except Exception:
        target.unlink(missing_ok=True)
        session.rollback()
        raise

    recorded = _audit(
        request, actor_id=user.id, action="report.attachment.uploaded",
        resource_type="report", resource_id=report.id,
        details={"attachment_id": str(attachment.id), "mime_type": mime_type},
    )
    return {
        "data": {
            "id": str(attachment.id), "filename": safe_name,
            "mime_type": mime_type, "size_bytes": len(content),
        },
        "meta": {"audit_event_recorded": recorded},
    }


@citizen_router.post(
    "/citizen/reports/{report_id}/attachments", status_code=status.HTTP_201_CREATED
)
async def upload_report_attachment(
    report_id: UUID,
    request: Request,
    file: Annotated[UploadFile, File()],
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _store_attachment(report_id, request, file, session, user)


def _attachment_file(session: Session, report_id: UUID, attachment_id: UUID):
    attachment = session.scalar(
        select(ReportAttachment).where(
            ReportAttachment.id == attachment_id,
            ReportAttachment.report_id == report_id,
            ReportAttachment.upload_status == "READY",
        )
    )
    if attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found.")
    root = get_settings().uploads_dir.resolve()
    target = (root / attachment.storage_key).resolve()
    if target.parent != root or not target.is_file():
        raise HTTPException(status_code=404, detail="Attachment not found.")
    return FileResponse(
        target,
        media_type=attachment.verified_mime_type,
        filename=attachment.original_filename or "attachment",
        headers={"X-Content-Type-Options": "nosniff"},
    )


@citizen_router.get(
    "/citizen/reports/{report_id}/attachments/{attachment_id}"
)
def download_my_report_attachment(
    report_id: UUID,
    attachment_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_report(session, report_id, user.id)
    return _attachment_file(session, report_id, attachment_id)


@admin_router.get("/reports")
def admin_list_reports(
    status_filter: str | None = Query(default=None, alias="status"),
    category_code: str | None = None,
    q: str | None = Query(default=None, max_length=120),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=MAX_PAGE_SIZE),
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    query = select(Report)
    if status_filter:
        if status_filter not in VALID_WORKFLOW:
            raise HTTPException(status_code=422, detail="Invalid report status filter.")
        query = query.where(Report.status == status_filter)
    if category_code:
        category = session.scalar(
            select(IncidentCategory).where(
                IncidentCategory.category_code == category_code,
                IncidentCategory.is_active.is_(True),
            )
        )
        if category is None:
            raise HTTPException(status_code=422, detail="Unknown category code.")
        query = query.where(Report.final_category_id == category.id)
    if q:
        query = query.where(Report.raw_content.ilike(f"%{q.strip()}%"))

    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = session.scalars(
        query.order_by(desc(Report.created_at))
        .offset((page - 1) * page_size).limit(page_size)
    ).all()
    category_ids = [row.final_category_id for row in rows if row.final_category_id]
    categories = {}
    if category_ids:
        categories = {
            item.id: item for item in session.scalars(
                select(IncidentCategory).where(IncidentCategory.id.in_(category_ids))
            ).all()
        }
    return {
        "data": [
            _report_payload(
                row, categories.get(row.final_category_id), include_owner=True
            ) for row in rows
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@admin_router.get("/reports/{report_id}/predictions")
def admin_list_predictions(
    report_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    if session.get(Report, report_id) is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    rows = session.scalars(
        select(Prediction).where(Prediction.report_id == report_id)
        .order_by(desc(Prediction.created_at))
    ).all()
    data = []
    for row in rows:
        category = (
            session.get(IncidentCategory, row.predicted_category_id)
            if row.predicted_category_id else None
        )
        model = session.get(ModelVersion, row.model_version_id) if row.model_version_id else None
        data.append({
            "id": str(row.id),
            "predicted_category": _category_payload(category),
            "confidence_value": float(row.confidence_value) if row.confidence_value is not None else None,
            "confidence_type": row.confidence_type,
            "model_version": model.version_label if model else None,
            "inference_status": row.inference_status,
            "needs_review": row.needs_review,
            "created_at": row.created_at.isoformat(),
        })
    return {"data": data}


def _attachment_file_for_admin(
    session: Session, report_id: UUID, attachment_id: UUID
):
    return _attachment_file(session, report_id, attachment_id)


@admin_router.get(
    "/reports/{report_id}/attachments/{attachment_id}"
)
def download_admin_report_attachment(
    report_id: UUID,
    attachment_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    if session.get(Report, report_id) is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return _attachment_file_for_admin(session, report_id, attachment_id)


@admin_router.get("/reports/{report_id}")
def admin_get_report(
    report_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    report = session.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    category = session.get(IncidentCategory, report.final_category_id) if report.final_category_id else None
    attachments = session.scalars(
        select(ReportAttachment).where(ReportAttachment.report_id == report.id)
    ).all()
    predictions = session.scalars(
        select(Prediction).where(Prediction.report_id == report.id)
        .order_by(desc(Prediction.created_at))
    ).all()
    return {
        "data": _report_payload(report, category, include_owner=True),
        "attachments": [
            {
                "id": str(item.id), "filename": item.original_filename,
                "mime_type": item.verified_mime_type,
                "size_bytes": item.file_size_bytes, "status": item.upload_status,
            } for item in attachments
        ],
        "predictions": [
            {
                "id": str(item.id),
                "inference_status": item.inference_status,
                "predicted_category_id": str(item.predicted_category_id) if item.predicted_category_id else None,
                "confidence_value": float(item.confidence_value) if item.confidence_value is not None else None,
                "confidence_type": item.confidence_type,
                "needs_review": item.needs_review,
                "created_at": item.created_at.isoformat(),
            } for item in predictions
        ],
    }


@admin_router.post("/reports/{report_id}/reviews", status_code=status.HTTP_201_CREATED)
def create_review(
    report_id: UUID,
    payload: ReviewCreate,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    report = session.scalar(
        select(Report).where(Report.id == report_id).with_for_update()
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    category = session.scalar(
        select(IncidentCategory).where(
            IncidentCategory.category_code == payload.category_code,
            IncidentCategory.is_active.is_(True),
        )
    )
    if category is None:
        raise HTTPException(status_code=422, detail="Unknown or inactive category.")

    if payload.prediction_id:
        prediction = session.scalar(
            select(Prediction).where(
                Prediction.id == payload.prediction_id,
                Prediction.report_id == report.id,
            )
        )
    else:
        prediction = session.scalar(
            select(Prediction).where(Prediction.report_id == report.id)
            .order_by(desc(Prediction.created_at)).limit(1)
        )
    if prediction is None:
        raise HTTPException(
            status_code=409, detail="No prediction record exists for this report."
        )

    previous_category_id = report.final_category_id or prediction.predicted_category_id
    action_code = "CONFIRMED" if prediction.predicted_category_id == category.id else "CORRECTED"
    review = PredictionReview(
        report_id=report.id, prediction_id=prediction.id,
        reviewer_id=staff.id, previous_category_id=previous_category_id,
        selected_category_id=category.id, action_code=action_code,
        note=payload.note.strip() if payload.note else None,
    )
    try:
        # Flush the append-only history row first. PostgreSQL verifies that the
        # final-category change is paired with this reviewer in the same xact.
        session.add(review)
        session.flush()
        report.final_category_id = category.id
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(review)

    recorded = _audit(
        request, actor_id=staff.id, action="report.reviewed",
        resource_type="report", resource_id=report_id,
        details={
            "review_id": str(review.id), "prediction_id": str(prediction.id),
            "action_code": action_code,
            "selected_category_code": payload.category_code,
        },
    )
    return {
        "data": {
            "id": str(review.id), "action_code": action_code,
            "selected_category": _category_payload(category),
            "previous_category_id": str(previous_category_id) if previous_category_id else None,
        },
        "meta": {"audit_event_recorded": recorded},
    }


@admin_router.get("/reports/{report_id}/reviews")
def list_reviews(
    report_id: UUID,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    if session.get(Report, report_id) is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    rows = session.scalars(
        select(PredictionReview).where(PredictionReview.report_id == report_id)
        .order_by(PredictionReview.reviewed_at, PredictionReview.created_at)
    ).all()
    data = []
    for row in rows:
        category = session.get(IncidentCategory, row.selected_category_id)
        reviewer = session.get(User, row.reviewer_id)
        data.append({
            "id": str(row.id), "prediction_id": str(row.prediction_id),
            "reviewer": reviewer.display_name if reviewer else None,
            "selected_category": _category_payload(category),
            "action_code": row.action_code, "note": row.note,
            "reviewed_at": row.reviewed_at.isoformat(),
        })
    return {"data": data}


@admin_router.patch("/reports/{report_id}/status")
def change_report_status(
    report_id: UUID,
    payload: StatusPatch,
    request: Request,
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    report = session.scalar(
        select(Report).where(Report.id == report_id).with_for_update()
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    allowed = set(VALID_WORKFLOW.get(report.status, set()))
    if report.status == "RESOLVED" and payload.status == "IN_PROGRESS":
        if "ADMIN" not in set(staff.role_codes or []):
            raise HTTPException(status_code=403, detail="Only ADMIN can reopen a resolved report.")
        allowed.add("IN_PROGRESS")
    if payload.status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"Transition {report.status} -> {payload.status} is not allowed.",
        )
    previous = report.status
    report.status = payload.status
    session.commit()

    recorded = _audit(
        request, actor_id=staff.id, action="report.status.changed",
        resource_type="report", resource_id=report_id,
        details={"from_status": previous, "to_status": payload.status},
    )
    return {
        "data": {"id": str(report_id), "from_status": previous, "status": payload.status},
        "meta": {"audit_event_recorded": recorded},
    }


@admin_router.get("/map/reports")
def admin_map_reports(
    status_filter: str | None = Query(default=None, alias="status"),
    category_code: str | None = None,
    page_size: int = Query(default=1000, ge=1, le=5000),
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    query = select(Report).where(
        Report.latitude.is_not(None), Report.longitude.is_not(None)
    )
    if status_filter:
        if status_filter not in VALID_WORKFLOW:
            raise HTTPException(status_code=422, detail="Invalid report status filter.")
        query = query.where(Report.status == status_filter)
    if category_code:
        category = session.scalar(
            select(IncidentCategory).where(IncidentCategory.category_code == category_code)
        )
        if category is None:
            raise HTTPException(status_code=422, detail="Unknown category code.")
        query = query.where(Report.final_category_id == category.id)
    rows = session.scalars(
        query.order_by(desc(Report.created_at)).limit(page_size)
    ).all()
    return {
        "data": [
            {
                "id": str(row.id), "latitude": float(row.latitude),
                "longitude": float(row.longitude), "status": row.status,
                "final_category_id": str(row.final_category_id) if row.final_category_id else None,
                "submitted_at": row.submitted_at.isoformat(),
            } for row in rows
        ],
        "meta": {"count": len(rows), "limit": page_size},
    }
