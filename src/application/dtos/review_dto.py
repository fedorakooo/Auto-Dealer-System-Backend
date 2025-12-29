from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ReviewCreateDTO:
    customer_id: UUID
    model_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None


@dataclass
class ReviewUpdateDTO:
    rating: int | None = None
    title: str | None = None
    comment: str | None = None


@dataclass
class ReviewDTO:
    id: UUID
    customer_id: UUID
    model_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
