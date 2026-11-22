from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class DealershipReviewComment:
    """Comment on a dealership review."""

    id: UUID
    review_id: UUID
    author_user_id: UUID
    body: str
    is_official: bool = False
    author_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DealershipReview:
    """Customer review of a dealership."""

    id: UUID
    dealership_id: int
    customer_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    is_hidden: bool = False
    author_name: str | None = None
    is_verified_customer: bool = False
    comments: list[DealershipReviewComment] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DealershipRatingSummary:
    """Aggregated rating of a dealership."""

    dealership_id: int
    reviews_count: int = 0
    average_rating: Decimal | None = None
    distribution: dict[int, int] = field(default_factory=lambda: dict.fromkeys(range(1, 6), 0))
