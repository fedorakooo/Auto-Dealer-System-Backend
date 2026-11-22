from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.vehicle_status import VehicleStatus


@dataclass
class VehicleCreateDTO:
    """Data for creating a vehicle."""

    trim_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    status: VehicleStatus = VehicleStatus.IN_STOCK


@dataclass
class VehicleUpdateDTO:
    """Data for updating a vehicle."""

    trim_id: UUID | None = None
    dealership_id: int | None = None
    vin: str | None = None
    production_year: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    price: Decimal | None = None
    status: VehicleStatus | None = None


@dataclass
class VehicleDTO:
    """Vehicle data returned by the application layer."""

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
    model_name: str | None = None
    trim_name: str | None = None
    images: list[str] | None = None  # photos of this exact vehicle
    model_images: list[str] | None = None  # model appearance, used as fallback
