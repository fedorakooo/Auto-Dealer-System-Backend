"""Pydantic models for order API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.order_dto import OrderCreateDTO, OrderDTO, OrderUpdateDTO
from src.domain.value_objects.order_status import OrderStatus


class OrderCreateRequest(BaseModel):
    """Request body for creating an order."""

    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    final_price: Decimal = Decimal("0.00")

    def to_dto(self) -> OrderCreateDTO:
        """Converts the request to a create DTO."""
        return OrderCreateDTO(
            customer_id=self.customer_id,
            vehicle_id=self.vehicle_id,
            dealership_id=self.dealership_id,
            final_price=self.final_price,
        )


class OrderUpdateRequest(BaseModel):
    """Request body for updating an order; the status has its own endpoint."""

    final_price: Decimal | None = Field(None, gt=0)

    def to_dto(self) -> OrderUpdateDTO:
        """Converts the request to an update DTO."""
        return OrderUpdateDTO(final_price=self.final_price)


class OrderResponse(BaseModel):
    """Single order response model."""

    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    model_id: UUID | None = None
    dealership_id: int
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    final_price: Decimal = Decimal("0.00")
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, order: OrderDTO) -> "OrderResponse":
        """Builds the response from an order DTO."""
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            vehicle_id=order.vehicle_id,
            model_id=order.model_id,
            dealership_id=order.dealership_id,
            status=order.status,
            final_price=order.final_price,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


class OrdersResponse(BaseModel):
    """Paginated orders response."""

    orders: list[OrderResponse]
    total: int


class OrderStatusUpdateRequest(BaseModel):
    """Request body for updating order status."""

    status: OrderStatus
