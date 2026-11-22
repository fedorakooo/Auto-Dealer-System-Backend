from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.vehicle_status import VehicleStatus


@dataclass
class Vehicle:
    """Physical vehicle of a model trim held by a dealership."""

    id: UUID
    model_id: UUID
    trim_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    status: VehicleStatus = VehicleStatus.IN_STOCK
    created_at: datetime | None = None
    updated_at: datetime | None = None
