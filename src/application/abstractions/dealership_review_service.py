from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.dealership_review_dto import (
    DealershipReviewCommentDTO,
    DealershipReviewCreateDTO,
    DealershipReviewDTO,
    DealershipReviewPageDTO,
    DealershipReviewUpdateDTO,
)
from src.domain.entities.user import User


class IDealershipReviewService(ABC):
    """Interface for dealership reviews, their moderation and comment threads."""

    @abstractmethod
    async def list_reviews(
        self, dealership_id: int, viewer: User | None, include_hidden: bool, page: int, limit: int
    ) -> DealershipReviewPageDTO:
        """Page of reviews with comments and the rating summary; hidden ones only for the dealership's staff."""

    @abstractmethod
    async def create_review(
        self, dealership_id: int, create_dto: DealershipReviewCreateDTO, requesting_user: User
    ) -> DealershipReviewDTO:
        """Create the customer's single review of a dealership."""

    @abstractmethod
    async def update_review(
        self, dealership_id: int, review_id: UUID, update_dto: DealershipReviewUpdateDTO, requesting_user: User
    ) -> DealershipReviewDTO:
        """Edit an own review."""

    @abstractmethod
    async def delete_review(self, dealership_id: int, review_id: UUID, requesting_user: User) -> None:
        """Delete a review; allowed to its author and to an admin."""

    @abstractmethod
    async def set_review_visibility(
        self, dealership_id: int, review_id: UUID, is_hidden: bool, requesting_user: User
    ) -> DealershipReviewDTO:
        """Hide or show a review; allowed to the dealership's staff."""

    @abstractmethod
    async def add_comment(
        self, dealership_id: int, review_id: UUID, body: str, requesting_user: User
    ) -> DealershipReviewCommentDTO:
        """Comment under a review: by its author, or an official reply by the dealership's staff."""

    @abstractmethod
    async def delete_comment(
        self, dealership_id: int, review_id: UUID, comment_id: UUID, requesting_user: User
    ) -> None:
        """Delete a comment; allowed to its author and to the dealership's staff."""
