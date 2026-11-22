from typing import Annotated

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
from src.application.abstractions.dealership_service import IDealershipService
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
    requesting_user: Annotated[User, Depends(get_current_user)],
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> DealershipResponse:
    """Creates a dealership."""
    dto = await dealership_service.create_dealership(body.to_dto())
    return DealershipResponse.from_dto(dto)


@router.get(
    "/{dealership_id:int}",
    response_model=DealershipResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_dealership(
    dealership_id: int,
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> DealershipResponse:
    """Returns a dealership by ID."""
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
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> DealershipsResponse:
    """Lists dealerships with filtering and pagination."""
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
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> list[DealershipResponse]:
    """Lists active dealerships."""
    dealerships = await dealership_service.get_active_dealerships()
    return [DealershipResponse.from_dto(d) for d in dealerships]


@router.get(
    "/managed",
    response_model=list[DealershipResponse],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Staff only"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_managed_dealerships(
    requesting_user: Annotated[User, Depends(get_current_user)],
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> list[DealershipResponse]:
    """Dealerships the user may manage: every one for an admin, the own one for an employee."""
    dealerships = await dealership_service.get_managed_dealerships(requesting_user)
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
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> list[DealershipResponse]:
    """Lists dealerships in a city."""
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
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> list[DealershipResponse]:
    """Lists dealerships in a country."""
    dealerships = await dealership_service.get_dealerships_by_country(country)
    return [DealershipResponse.from_dto(d) for d in dealerships]


@router.patch(
    "/{dealership_id:int}",
    response_model=DealershipResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Only an admin or an employee of this dealership"},
        status.HTTP_404_NOT_FOUND: {"description": "Dealership or city not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_dealership(
    dealership_id: int,
    body: DealershipUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> DealershipResponse:
    """Updates a dealership."""
    dto = await dealership_service.update_dealership(dealership_id, body.to_dto(), requesting_user)
    return DealershipResponse.from_dto(dto)


@router.delete(
    "/{dealership_id:int}",
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
    requesting_user: Annotated[User, Depends(get_current_user)],
    dealership_service: Annotated[IDealershipService, Depends(get_dealership_service)],
) -> None:
    """Deletes a dealership."""
    await dealership_service.delete_dealership(dealership_id)
    return None
