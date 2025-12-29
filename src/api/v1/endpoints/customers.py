from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_customer_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.customer_models import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
)
from src.application.services.customer_service import CustomerService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Customer already exists for this user"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_customer(
    body: CustomerCreateRequest,
    requesting_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    dto = await customer_service.create_customer(body.to_dto())
    return CustomerResponse.from_dto(dto)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_customer(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    dto = await customer_service.get_customer(customer_id)
    return CustomerResponse.from_dto(dto)


@router.get(
    "/user/{user_id}",
    response_model=CustomerResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_customer_by_user_id(
    user_id: UUID,
    requesting_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    dto = await customer_service.get_customer_by_user_id(user_id)
    return CustomerResponse.from_dto(dto)


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_customer(
    customer_id: UUID,
    body: CustomerUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    dto = await customer_service.update_customer(customer_id, body.to_dto())
    return CustomerResponse.from_dto(dto)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_customer(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service),
) -> None:
    await customer_service.delete_customer(customer_id)
    return None
