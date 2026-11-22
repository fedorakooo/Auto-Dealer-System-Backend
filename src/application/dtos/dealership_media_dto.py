from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.media_type import MediaType


@dataclass
class DealershipMediaUpdateDTO:
    """Data for updating dealership photo metadata."""

    description: str | None = None
    sort_order: int | None = None


@dataclass
class DealershipMediaDTO:
    """Dealership photo data returned by the application layer."""

    id: UUID
    dealership_id: int
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None
