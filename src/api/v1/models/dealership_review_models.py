"""Pydantic models for dealership reviews, moderation and comments."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.dealership_review_dto import (
    DealershipRatingSummaryDTO,
    DealershipReviewCommentDTO,
    DealershipReviewCreateDTO,
    DealershipReviewDTO,
    DealershipReviewPageDTO,
    DealershipReviewUpdateDTO,
)


class DealershipReviewCreateRequest(BaseModel):
    """Request body for creating a dealership review."""

    rating: int = Field(ge=1, le=5)
    title: str | None = Field(None, max_length=255)
    comment: str | None = Field(None, max_length=5000)

    def to_dto(self) -> DealershipReviewCreateDTO:
        """Converts the request to a create DTO."""
        return DealershipReviewCreateDTO(rating=self.rating, title=self.title, comment=self.comment)


class DealershipReviewUpdateRequest(BaseModel):
    """Request body for updating a dealership review."""

    rating: int | None = Field(None, ge=1, le=5)
    title: str | None = Field(None, max_length=255, description="Blank text clears the title")
    comment: str | None = Field(None, max_length=5000, description="Blank text clears the comment")

    def to_dto(self) -> DealershipReviewUpdateDTO:
        """Converts the request to an update DTO."""
        return DealershipReviewUpdateDTO(rating=self.rating, title=self.title, comment=self.comment)


class DealershipReviewVisibilityRequest(BaseModel):
    """Request body for hiding or showing a dealership review."""

    is_hidden: bool


class DealershipReviewCommentCreateRequest(BaseModel):
    """Request body for commenting on a dealership review."""

    body: str = Field(min_length=1, max_length=2000)


class DealershipReviewCommentResponse(BaseModel):
    """Dealership review comment returned by the API."""

    id: UUID
    review_id: UUID
    author_user_id: UUID
    author_name: str | None = None
    body: str
    is_official: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, comment: DealershipReviewCommentDTO) -> "DealershipReviewCommentResponse":
        """Builds the response from a review comment DTO."""
        return cls(
            id=comment.id,
            review_id=comment.review_id,
            author_user_id=comment.author_user_id,
            author_name=comment.author_name,
            body=comment.body,
            is_official=comment.is_official,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )


class DealershipReviewResponse(BaseModel):
    """Dealership review returned by the API."""

    id: UUID
    dealership_id: int
    customer_id: UUID
    author_name: str | None = None
    is_verified_customer: bool = False
    rating: int
    title: str | None = None
    comment: str | None = None
    is_hidden: bool = False
    comments: list[DealershipReviewCommentResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, review: DealershipReviewDTO) -> "DealershipReviewResponse":
        """Builds the response from a review DTO."""
        return cls(
            id=review.id,
            dealership_id=review.dealership_id,
            customer_id=review.customer_id,
            author_name=review.author_name,
            is_verified_customer=review.is_verified_customer,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            is_hidden=review.is_hidden,
            comments=[DealershipReviewCommentResponse.from_dto(c) for c in review.comments],
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


class DealershipRatingSummaryResponse(BaseModel):
    """Aggregated rating of a dealership."""

    reviews_count: int
    average_rating: Decimal | None = None
    distribution: dict[int, int]

    @classmethod
    def from_dto(cls, summary: DealershipRatingSummaryDTO) -> "DealershipRatingSummaryResponse":
        """Builds the response from a rating summary DTO."""
        return cls(
            reviews_count=summary.reviews_count,
            average_rating=summary.average_rating,
            distribution=summary.distribution,
        )


class DealershipReviewsResponse(BaseModel):
    """Page of dealership reviews with the rating summary."""

    reviews: list[DealershipReviewResponse]
    total: int
    summary: DealershipRatingSummaryResponse

    @classmethod
    def from_dto(cls, page: DealershipReviewPageDTO) -> "DealershipReviewsResponse":
        """Builds the response from a review page DTO."""
        return cls(
            reviews=[DealershipReviewResponse.from_dto(r) for r in page.reviews],
            total=page.total,
            summary=DealershipRatingSummaryResponse.from_dto(page.summary),
        )
