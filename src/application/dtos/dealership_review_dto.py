from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class DealershipReviewCreateDTO:
    """Data for creating a dealership review."""

    rating: int
    title: str | None = None
    comment: str | None = None


@dataclass
class DealershipReviewUpdateDTO:
    """Data for updating a dealership review."""

    rating: int | None = None
    title: str | None = None
    comment: str | None = None


@dataclass
class DealershipReviewCommentDTO:
    """Dealership review comment data."""

    id: UUID
    review_id: UUID
    author_user_id: UUID
    body: str
    is_official: bool = False
    author_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DealershipReviewDTO:
    """Dealership review data with its comments."""

    id: UUID
    dealership_id: int
    customer_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    is_hidden: bool = False
    author_name: str | None = None
    is_verified_customer: bool = False
    comments: list[DealershipReviewCommentDTO] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class DealershipRatingSummaryDTO:
    """Aggregated rating of a dealership."""

    reviews_count: int = 0
    average_rating: Decimal | None = None
    distribution: dict[int, int] = field(default_factory=lambda: dict.fromkeys(range(1, 6), 0))


@dataclass
class DealershipReviewPageDTO:
    """Page of dealership reviews with the rating summary."""

    reviews: list[DealershipReviewDTO]
    total: int
    summary: DealershipRatingSummaryDTO
