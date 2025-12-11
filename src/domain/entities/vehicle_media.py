from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.media_type import MediaType


@dataclass
class VehicleMedia:
    id: UUID
    vehicle_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None
