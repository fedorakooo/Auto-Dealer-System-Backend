from fastapi import APIRouter, Depends, status

from src.api.dependencies.database import get_database_health_check
from src.domain.abstractions.database.healthcheck import IDatabaseHealthCheck
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Service is healthy"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def health_check() -> dict[str, str]:
    logger.debug("Health check endpoint called")
    return {"status": "ok"}


@router.get("/database", status_code=status.HTTP_200_OK)
async def database_health_check(
    health_check: IDatabaseHealthCheck = Depends(get_database_health_check),
) -> dict[str, str]:
    await health_check.check_health()
    return {"status": "ok", "component": "postgresql"}
