from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Model:
    """Vehicle model entity."""

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
