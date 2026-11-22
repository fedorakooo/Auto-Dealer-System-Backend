from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ModelCreateDTO:
    """Data for creating a vehicle model."""

    body_type_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None


@dataclass
class ModelUpdateDTO:
    """Data for updating a vehicle model."""

    body_type_id: int | None = None
    name: str | None = None
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int | None = None
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None


@dataclass
class ModelDTO:
    """Vehicle model data returned by the application layer."""

    id: UUID
    body_type_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    images: list[str] | None = None  # model appearance photos
    vehicles_in_stock: int = 0
    min_price: Decimal | None = None  # lowest price among in-stock vehicles
