from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Review:
    id: UUID
    customer_id: UUID
    model_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
