import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.database import check_database_connection

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness probe")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready", summary="Readiness probe")
def readiness() -> dict[str, object]:
    try:
        check_database_connection()
    except SQLAlchemyError:
        logger.warning("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": "unavailable"},
        ) from None

    return {"status": "ready", "checks": {"database": "ok"}}
