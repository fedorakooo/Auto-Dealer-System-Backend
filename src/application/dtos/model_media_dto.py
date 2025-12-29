from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.media_type import MediaType


@dataclass
class ModelMediaCreateDTO:
    model_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0


@dataclass
class ModelMediaUpdateDTO:
    url: str | None = None
    media_type: MediaType | None = None
    description: str | None = None
    sort_order: int | None = None


@dataclass
class ModelMediaDTO:
    id: UUID
    model_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None
