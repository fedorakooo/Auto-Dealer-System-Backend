from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_custom_order_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.custom_order_models import (
    CustomOrderCreateRequest,
    CustomOrderResponse,
    CustomOrdersResponse,
    CustomOrderStatusUpdateRequest,
    CustomOrderUpdateRequest,
)
from src.application.services.custom_order_service import CustomOrderService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/custom-orders", tags=["Сustom-orders"])


@router.post(
    "",
    response_model=CustomOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer, model, engine, transmission or dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_custom_order(
    body: CustomOrderCreateRequest,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrderResponse:
    dto = await custom_order_service.create_custom_order(body.to_dto())
    return CustomOrderResponse.from_dto(dto)


@router.get(
    "/{custom_order_id}",
    response_model=CustomOrderResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_custom_order(
    custom_order_id: UUID,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrderResponse:
    dto = await custom_order_service.get_custom_order(custom_order_id)
    return CustomOrderResponse.from_dto(dto)


@router.get(
    "/customer/{customer_id}",
    response_model=CustomOrdersResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_custom_orders_by_customer(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrdersResponse:
    orders = await custom_order_service.get_custom_orders_by_customer(customer_id)
    return CustomOrdersResponse(custom_orders=[CustomOrderResponse.from_dto(o) for o in orders])


@router.get(
    "/dealership/{dealership_id}",
    response_model=CustomOrdersResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_custom_orders_by_dealership(
    dealership_id: int,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrdersResponse:
    orders = await custom_order_service.get_custom_orders_by_dealership(dealership_id)
    return CustomOrdersResponse(custom_orders=[CustomOrderResponse.from_dto(o) for o in orders])


@router.patch(
    "/{custom_order_id}",
    response_model=CustomOrderResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order, model, engine or transmission not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_custom_order(
    custom_order_id: UUID,
    body: CustomOrderUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrderResponse:
    dto = await custom_order_service.update_custom_order(
        custom_order_id, body.to_dto(), current_user_id=requesting_user.id
    )
    return CustomOrderResponse.from_dto(dto)


@router.patch(
    "/{custom_order_id}/status",
    response_model=CustomOrderResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_custom_order_status(
    custom_order_id: UUID,
    body: CustomOrderStatusUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> CustomOrderResponse:
    dto = await custom_order_service.update_custom_order_status(
        custom_order_id, body.status, current_user_id=requesting_user.id
    )
    return CustomOrderResponse.from_dto(dto)


@router.delete(
    "/{custom_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_custom_order(
    custom_order_id: UUID,
    requesting_user: User = Depends(get_current_user),
    custom_order_service: CustomOrderService = Depends(get_custom_order_service),
) -> None:
    await custom_order_service.delete_custom_order(custom_order_id, current_user_id=requesting_user.id)
    return None
