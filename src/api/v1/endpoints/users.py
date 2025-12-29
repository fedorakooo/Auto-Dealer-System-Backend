from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_user_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.user_models import (
    UserCreateRequest,
    UserResponse,
    UsersResponse,
    UserUpdateRequest,
)
from src.application.services.user_service import UserService
from src.domain.entities.user import User
from src.domain.value_objects.filters import OrderField, UserFilter, UserSortField
from src.domain.value_objects.user_role import UserRole
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_409_CONFLICT: {"description": "User with given email or phone already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def create_user(
    body: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user (registration)."""
    logger.info(f"Creating user with email: {body.email}")
    dto = await user_service.create_user(body.to_dto())
    logger.info(f"User created successfully via endpoint: id={dto.id}, email={body.email}")
    return UserResponse.from_dto(dto)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    requesting_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user by ID (auth required)."""
    dto = await user_service.get_user(user_id)
    return UserResponse.from_dto(dto)


@router.get(
    "",
    response_model=UsersResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: UserSortField | None = Query(None),
    order_by: OrderField = Query(OrderField.ASC),
    email: str | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    user_service: UserService = Depends(get_user_service),
    requesting_user: User = Depends(get_current_user),
) -> UsersResponse:
    """List users with filtering and pagination."""
    user_filter = UserFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=order_by,
        email=email,
        role=role,
        is_active=is_active,
    )
    users, total = await user_service.get_users(user_filter)
    return UsersResponse(
        users=[UserResponse.from_dto(u) for u in users],
        total=total,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_409_CONFLICT: {"description": "Email or phone already in use"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_user(
    user_id: UUID,
    body: UserUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user profile (self or with privileges)."""
    dto = await user_service.update_user(user_id, body.to_dto(), current_user_id=requesting_user.id)
    return UserResponse.from_dto(dto)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_user(
    user_id: UUID,
    requesting_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Delete user (self or admin)."""
    await user_service.delete_user(user_id, current_user_id=requesting_user.id)
    return None
