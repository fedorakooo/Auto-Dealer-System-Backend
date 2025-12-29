from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.database import get_unit_of_work
from src.api.dependencies.services import get_order_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.order_models import (
    OrderCreateRequest,
    OrderResponse,
    OrdersResponse,
    OrderStatusUpdateRequest,
    OrderUpdateRequest,
)
from src.application.services.order_service import OrderService
from src.domain.entities.user import User
from src.domain.value_objects.filters import OrderFilter, OrderSortField
from src.domain.value_objects.user_role import UserRole
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer, vehicle or dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_order(
    body: OrderCreateRequest,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    logger.info(f"Creating order for vehicle_id={body.vehicle_id}, requested by user_id={requesting_user.id}")
    dto = await order_service.create_order(body.to_dto())
    logger.info(f"Order created successfully: id={dto.id}, vehicle_id={body.vehicle_id}")
    return OrderResponse.from_dto(dto)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_order(
    order_id: UUID,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    dto = await order_service.get_order(order_id)
    return OrderResponse.from_dto(dto)


@router.get(
    "",
    response_model=OrdersResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: OrderSortField | None = Query(None),
    order_by: str = Query("asc"),
    customer_id: UUID | None = Query(None),
    dealership_id: int | None = Query(None),
    order_status: str | None = Query(None, alias="status"),
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    uow=Depends(get_unit_of_work),
) -> OrdersResponse:
    from src.domain.value_objects.filters import OrderField

    # Для CUSTOMER автоматически фильтруем заказы по его customer_id
    final_customer_id = customer_id
    if requesting_user.role == UserRole.CUSTOMER:
        # Получаем customer_id из user_id
        async with uow:
            customer = await uow.customer_repository.get_by_user_id(requesting_user.id)
            if customer:
                final_customer_id = customer.id
                # Если customer_id был передан явно, проверяем что он соответствует текущему пользователю
                if customer_id and customer.id != customer_id:
                    from fastapi import HTTPException

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own orders"
                    )
            else:
                # Если customer не найден, возвращаем пустой список
                return OrdersResponse(orders=[], total=0)

    order_filter = OrderFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=OrderField(order_by.lower()),
        customer_id=str(final_customer_id) if final_customer_id else None,
        dealership_id=dealership_id,
        status=order_status,
    )
    orders, total = await order_service.get_orders(order_filter)
    return OrdersResponse(
        orders=[OrderResponse.from_dto(o) for o in orders],
        total=total,
    )


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderResponse],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_orders_by_customer(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    orders = await order_service.get_orders_by_customer(customer_id)
    return [OrderResponse.from_dto(o) for o in orders]


@router.get(
    "/dealership/{dealership_id}",
    response_model=list[OrderResponse],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_orders_by_dealership(
    dealership_id: int,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    orders = await order_service.get_orders_by_dealership(dealership_id)
    return [OrderResponse.from_dto(o) for o in orders]


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Order, vehicle or dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def update_order(
    order_id: UUID,
    body: OrderUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    dto = await order_service.update_order(order_id, body.to_dto(), current_user_id=requesting_user.id)
    return OrderResponse.from_dto(dto)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid status transition"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def update_order_status(
    order_id: UUID,
    body: OrderStatusUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    dto = await order_service.update_order_status(order_id, body.status, current_user_id=requesting_user.id)
    return OrderResponse.from_dto(dto)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_order(
    order_id: UUID,
    requesting_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> None:
    await order_service.delete_order(order_id, current_user_id=requesting_user.id)
    return None
