from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_roles
from app.api.reports import VALID_WORKFLOW, _category_payload
from app.db.models import IncidentCategory, Prediction, Report, User

router = APIRouter(prefix="/api/v1/admin", tags=["admin dashboard"])


@router.get("/categories")
def list_admin_categories(
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    rows = session.scalars(
        select(IncidentCategory)
        .where(IncidentCategory.is_active.is_(True))
        .order_by(IncidentCategory.sort_order)
    ).all()
    return {"data": [_category_payload(row) for row in rows]}


@router.get("/dashboard/summary")
def dashboard_summary(
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    total = session.scalar(select(func.count()).select_from(Report)) or 0
    status_rows = session.execute(
        select(Report.status, func.count(Report.id)).group_by(Report.status)
    ).all()
    pending = session.scalar(
        select(func.count()).select_from(Prediction)
        .where(Prediction.needs_review.is_(True))
    ) or 0
    status_counts = {key: 0 for key in VALID_WORKFLOW}
    status_counts.update({key: count for key, count in status_rows})
    return {"data": {
        "total_reports": total,
        "pending_reviews": pending,
        "status_counts": status_counts,
    }}


@router.get("/dashboard/categories")
def dashboard_categories(
    session: Session = Depends(get_db),
    staff: User = Depends(require_roles("RECEIVER", "ADMIN")),
):
    rows = session.execute(
        select(IncidentCategory, func.count(Report.id).label("report_count"))
        .outerjoin(Report, Report.final_category_id == IncidentCategory.id)
        .where(IncidentCategory.is_active.is_(True))
        .group_by(IncidentCategory.id)
        .order_by(IncidentCategory.sort_order)
    ).all()
    return {"data": [
        {**_category_payload(category), "report_count": count}
        for category, count in rows
    ]}
