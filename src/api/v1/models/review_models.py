"""Pydantic models for review API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.review_dto import ReviewCreateDTO, ReviewDTO, ReviewUpdateDTO


class ReviewCreateRequest(BaseModel):
    """Request body for creating a review."""

    customer_id: UUID
    model_id: UUID
    rating: int = Field(ge=1, le=5)
    title: str | None = None
    comment: str | None = None

    def to_dto(self) -> ReviewCreateDTO:
        return ReviewCreateDTO(
            customer_id=self.customer_id,
            model_id=self.model_id,
            rating=self.rating,
            title=self.title,
            comment=self.comment,
        )


class ReviewUpdateRequest(BaseModel):
    """Request body for updating a review."""

    rating: int | None = Field(None, ge=1, le=5)
    title: str | None = None
    comment: str | None = None

    def to_dto(self) -> ReviewUpdateDTO:
        return ReviewUpdateDTO(
            rating=self.rating,
            title=self.title,
            comment=self.comment,
        )


class ReviewResponse(BaseModel):
    """Single review response model."""

    id: UUID
    customer_id: UUID
    model_id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, review: ReviewDTO) -> "ReviewResponse":
        return cls(
            id=review.id,
            customer_id=review.customer_id,
            model_id=review.model_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


class ReviewsResponse(BaseModel):
    """List of reviews response."""

    reviews: list[ReviewResponse]
