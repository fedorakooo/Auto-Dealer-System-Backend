from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.order_status import OrderStatus


@dataclass
class Order:
    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    final_price: Decimal = Decimal("0.00")
    created_at: datetime | None = None
    updated_at: datetime | None = None
