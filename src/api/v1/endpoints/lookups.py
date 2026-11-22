from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies.services import get_lookup_service
from src.api.v1.models.lookup_models import LookupsResponse
from src.application.abstractions.lookup_service import ILookupService

router = APIRouter(prefix="/lookups", tags=["Lookups"])


@router.get(
    "",
    response_model=LookupsResponse,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"}},
)
async def get_lookups(
    response: Response,
    lookup_service: Annotated[ILookupService, Depends(get_lookup_service)],
) -> LookupsResponse:
    """Body types, engines, transmissions and enum codes used by catalog filters and forms."""
    response.headers["Cache-Control"] = "public, max-age=60"
    return LookupsResponse.from_dto(await lookup_service.get_lookups())
