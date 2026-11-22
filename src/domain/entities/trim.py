from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects.drive_type import DriveType


@dataclass
class Trim:
    """Trim (equipment level) of a vehicle model."""

    id: UUID
    model_id: UUID
    name: str
    engine_id: int
    transmission_id: int
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
