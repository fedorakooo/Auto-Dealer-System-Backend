from fastapi import APIRouter, status

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
