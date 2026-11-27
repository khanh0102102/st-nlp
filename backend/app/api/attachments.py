from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.api.reports import _store_attachment
from app.db.models import User

router = APIRouter(prefix="/api/v1", tags=["attachments"])


@router.post("/attachments", status_code=201)
async def upload_attachment_compat(
    request: Request,
    report_id: Annotated[UUID, Form()],
    file: Annotated[UploadFile, File()],
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _store_attachment(report_id, request, file, session, user)
