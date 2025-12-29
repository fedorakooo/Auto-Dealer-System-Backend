from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.custom_order_status import CustomOrderStatus


@dataclass
class CustomOrderCreateDTO:
    customer_id: UUID
    dealership_id: int
    model_id: UUID
    engine_id: int
    transmission_id: int
    exterior_color: str
    interior_color: str | None = None
    estimated_price: Decimal | None = None
    notes: str | None = None


@dataclass
class CustomOrderUpdateDTO:
    model_id: UUID | None = None
    engine_id: int | None = None
    transmission_id: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    status: CustomOrderStatus | None = None
    estimated_price: Decimal | None = None
    final_price: Decimal | None = None
    notes: str | None = None


@dataclass
class CustomOrderDTO:
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
