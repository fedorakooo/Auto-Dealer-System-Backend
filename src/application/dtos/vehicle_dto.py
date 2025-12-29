from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class VehicleCreateDTO:
    model_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    is_active: bool = True


@dataclass
class VehicleUpdateDTO:
    model_id: UUID | None = None
    dealership_id: int | None = None
    vin: str | None = None
    production_year: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None


@dataclass
class VehicleDTO:
    id: UUID
    model_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_name: str | None = None
    images: list[str] | None = None  # URLs to model media images
