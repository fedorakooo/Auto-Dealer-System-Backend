from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_favorite_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.favorite_models import (
    FavoriteAddRequest,
    FavoriteRemoveRequest,
    FavoritesResponse,
)
from src.application.services.favorite_service import FavoriteService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Vehicle is already in favorites"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer or vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def add_favorite(
    body: FavoriteAddRequest,
    requesting_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
) -> None:
    await favorite_service.add_favorite(body.to_dto())
    return None


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Vehicle is not in favorites"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer or vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def remove_favorite(
    body: FavoriteRemoveRequest,
    requesting_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
) -> None:
    await favorite_service.remove_favorite(body.to_dto())
    return None


@router.get(
    "/customer/{customer_id}",
    response_model=FavoritesResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_favorites(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
) -> FavoritesResponse:
    vehicles = await favorite_service.get_favorites(customer_id)
    return FavoritesResponse.from_dtos(vehicles)
