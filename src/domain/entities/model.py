from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.drive_type import DriveType


@dataclass
class Model:
    id: UUID
    body_type_id: int
    engine_id: int
    transmission_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
