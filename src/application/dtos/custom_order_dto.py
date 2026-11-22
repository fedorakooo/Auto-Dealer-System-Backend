from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.custom_order_status import CustomOrderStatus


@dataclass
class CustomOrderCreateDTO:
    """Data for creating a custom order."""

    customer_id: UUID
    dealership_id: int
    trim_id: UUID
    exterior_color: str
    interior_color: str | None = None
    estimated_price: Decimal | None = None
    notes: str | None = None


@dataclass
class CustomOrderUpdateDTO:
    """Data for updating a custom order."""

    trim_id: UUID | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    status: CustomOrderStatus | None = None
    estimated_price: Decimal | None = None
    final_price: Decimal | None = None
    notes: str | None = None


@dataclass
class CustomOrderDTO:
    """Custom order data returned by the application layer."""

    id: UUID
    customer_id: UUID
    dealership_id: int
    model_id: UUID
    trim_id: UUID
    exterior_color: str
    interior_color: str | None = None
    status: CustomOrderStatus = CustomOrderStatus.PENDING_APPROVAL
    estimated_price: Decimal | None = None
    final_price: Decimal | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
