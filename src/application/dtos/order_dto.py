from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.order_status import OrderStatus


@dataclass
class OrderCreateDTO:
    """Data for creating an order."""

    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    final_price: Decimal = Decimal("0.00")


@dataclass
class OrderUpdateDTO:
    """Data for updating an order."""

    final_price: Decimal | None = None


@dataclass
class OrderDTO:
    """Order data returned by the application layer."""

    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    final_price: Decimal = Decimal("0.00")
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_id: UUID | None = None  # model of the vehicle, filled by the service
