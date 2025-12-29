from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_dealership_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.dealership_models import (
    DealershipCreateRequest,
    DealershipResponse,
    DealershipsResponse,
    DealershipUpdateRequest,
)
from src.application.services.dealership_service import DealershipService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/dealerships", tags=["dealerships"])


@router.post(
    "",
    response_model=DealershipResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "City not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_dealership(
    body: DealershipCreateRequest,
    requesting_user: User = Depends(get_current_user),
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> DealershipResponse:
    dto = await dealership_service.create_dealership(body.to_dto())
    return DealershipResponse.from_dto(dto)


@router.get(
    "/{dealership_id}",
    response_model=DealershipResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_dealership(
    dealership_id: int,
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> DealershipResponse:
    dto = await dealership_service.get_dealership(dealership_id)
    return DealershipResponse.from_dto(dto)


@router.get(
    "",
    response_model=DealershipsResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_dealerships(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> DealershipsResponse:
    dealerships, total = await dealership_service.get_all_dealerships(page=page, limit=limit)
    return DealershipsResponse(
        dealerships=[DealershipResponse.from_dto(d) for d in dealerships],
        total=total,
    )


@router.get(
    "/active",
    response_model=list[DealershipResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_active_dealerships(
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> list[DealershipResponse]:
    dealerships = await dealership_service.get_active_dealerships()
    return [DealershipResponse.from_dto(d) for d in dealerships]


@router.get(
    "/city/{city_id}",
    response_model=list[DealershipResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_dealerships_by_city(
    city_id: int,
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> list[DealershipResponse]:
    dealerships = await dealership_service.get_dealerships_by_city(city_id)
    return [DealershipResponse.from_dto(d) for d in dealerships]


@router.get(
    "/country/{country}",
    response_model=list[DealershipResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_dealerships_by_country(
    country: str,
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> list[DealershipResponse]:
    dealerships = await dealership_service.get_dealerships_by_country(country)
    return [DealershipResponse.from_dto(d) for d in dealerships]


@router.patch(
    "/{dealership_id}",
    response_model=DealershipResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Dealership or city not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_dealership(
    dealership_id: int,
    body: DealershipUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> DealershipResponse:
    dto = await dealership_service.update_dealership(dealership_id, body.to_dto())
    return DealershipResponse.from_dto(dto)


@router.delete(
    "/{dealership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_dealership(
    dealership_id: int,
    requesting_user: User = Depends(get_current_user),
    dealership_service: DealershipService = Depends(get_dealership_service),
) -> None:
    await dealership_service.delete_dealership(dealership_id)
    return None
