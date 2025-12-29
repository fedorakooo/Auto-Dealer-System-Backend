from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_city_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.city_models import (
    CitiesResponse,
    CityCreateRequest,
    CityResponse,
    CityUpdateRequest,
)
from src.application.services.city_service import CityService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/cities", tags=["Сities"])


@router.post(
    "",
    response_model=CityResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_city(
    body: CityCreateRequest,
    requesting_user: User = Depends(get_current_user),
    city_service: CityService = Depends(get_city_service),
) -> CityResponse:
    dto = await city_service.create_city(body.to_dto())
    return CityResponse.from_dto(dto)


@router.get(
    "/{city_id}",
    response_model=CityResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "City not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_city(
    city_id: int,
    city_service: CityService = Depends(get_city_service),
) -> CityResponse:
    dto = await city_service.get_city(city_id)
    return CityResponse.from_dto(dto)


@router.get(
    "",
    response_model=CitiesResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_cities(
    city_service: CityService = Depends(get_city_service),
) -> CitiesResponse:
    cities = await city_service.get_all_cities()
    return CitiesResponse(cities=[CityResponse.from_dto(c) for c in cities])


@router.patch(
    "/{city_id}",
    response_model=CityResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "City not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_city(
    city_id: int,
    body: CityUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    city_service: CityService = Depends(get_city_service),
) -> CityResponse:
    dto = await city_service.update_city(city_id, body.to_dto())
    return CityResponse.from_dto(dto)


@router.delete(
    "/{city_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "City not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_city(
    city_id: int,
    requesting_user: User = Depends(get_current_user),
    city_service: CityService = Depends(get_city_service),
) -> None:
    await city_service.delete_city(city_id)
    return None
