"""Pydantic models for custom order API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.custom_order_dto import (
    CustomOrderCreateDTO,
    CustomOrderDTO,
    CustomOrderUpdateDTO,
)
from src.domain.value_objects.custom_order_status import CustomOrderStatus


class CustomOrderCreateRequest(BaseModel):
    """Request body for creating a custom order."""

    customer_id: UUID
    dealership_id: int
    model_id: UUID
    engine_id: int
    transmission_id: int
    exterior_color: str
    interior_color: str | None = None
    estimated_price: Decimal | None = None
    notes: str | None = None

    def to_dto(self) -> CustomOrderCreateDTO:
        return CustomOrderCreateDTO(
            customer_id=self.customer_id,
            dealership_id=self.dealership_id,
            model_id=self.model_id,
            engine_id=self.engine_id,
            transmission_id=self.transmission_id,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            estimated_price=self.estimated_price,
            notes=self.notes,
        )


class CustomOrderUpdateRequest(BaseModel):
    """Request body for updating a custom order."""

    model_id: UUID | None = None
    engine_id: int | None = None
    transmission_id: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    status: CustomOrderStatus | None = None
    estimated_price: Decimal | None = None
    final_price: Decimal | None = None
    notes: str | None = None

    def to_dto(self) -> CustomOrderUpdateDTO:
        return CustomOrderUpdateDTO(
            model_id=self.model_id,
            engine_id=self.engine_id,
            transmission_id=self.transmission_id,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            status=self.status,
            estimated_price=self.estimated_price,
            final_price=self.final_price,
            notes=self.notes,
        )


class CustomOrderResponse(BaseModel):
    """Single custom order response model."""

    id: UUID
    customer_id: UUID
    dealership_id: int
    model_id: UUID
    engine_id: int
    transmission_id: int
    exterior_color: str
    interior_color: str | None = None
    status: CustomOrderStatus = CustomOrderStatus.PENDING_APPROVAL
    estimated_price: Decimal | None = None
    final_price: Decimal | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, custom_order: CustomOrderDTO) -> "CustomOrderResponse":
        return cls(
            id=custom_order.id,
            customer_id=custom_order.customer_id,
            dealership_id=custom_order.dealership_id,
            model_id=custom_order.model_id,
            engine_id=custom_order.engine_id,
            transmission_id=custom_order.transmission_id,
            exterior_color=custom_order.exterior_color,
            interior_color=custom_order.interior_color,
            status=custom_order.status,
            estimated_price=custom_order.estimated_price,
            final_price=custom_order.final_price,
            notes=custom_order.notes,
            created_at=custom_order.created_at,
            updated_at=custom_order.updated_at,
        )


class CustomOrdersResponse(BaseModel):
    """List of custom orders response."""

    custom_orders: list[CustomOrderResponse]


class CustomOrderStatusUpdateRequest(BaseModel):
    """Request body for updating custom order status."""

    status: CustomOrderStatus
