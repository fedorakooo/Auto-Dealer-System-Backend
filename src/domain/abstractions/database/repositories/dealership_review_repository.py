from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.dealership_review import (
    DealershipRatingSummary,
    DealershipReview,
    DealershipReviewComment,
)


class IDealershipReviewRepository(ABC):
    """Interface for dealership reviews and their comment threads."""

    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> DealershipReview | None:
        """Returns one review (without author details and comments) or None."""

    @abstractmethod
    async def get_by_dealership_and_customer(self, dealership_id: int, customer_id: UUID) -> DealershipReview | None:
        """Returns the review a customer left for a dealership or None."""

    @abstractmethod
    async def get_page(
        self,
        dealership_id: int,
        include_hidden: bool,
        viewer_customer_id: UUID | None,
        offset: int,
        limit: int,
    ) -> tuple[list[DealershipReview], int]:
        """Returns a page of reviews with author details and comments, and the total count."""

    @abstractmethod
    async def get_rating_summaries(self, dealership_ids: list[int]) -> dict[int, DealershipRatingSummary]:
        """Returns the rating of visible reviews keyed by dealership ID; dealerships without reviews are absent."""

    @abstractmethod
    async def create(self, review: DealershipReview) -> DealershipReview:
        """Creates a review."""

    @abstractmethod
    async def update(self, review: DealershipReview) -> DealershipReview:
        """Updates rating, title, comment and visibility of a review."""

    @abstractmethod
    async def delete(self, review_id: UUID) -> bool:
        """Deletes a review with its comments."""

    @abstractmethod
    async def get_comment(self, comment_id: UUID) -> DealershipReviewComment | None:
        """Returns one comment or None."""

    @abstractmethod
    async def create_comment(self, comment: DealershipReviewComment) -> DealershipReviewComment:
        """Creates a comment and returns it with the author name."""

    @abstractmethod
    async def delete_comment(self, comment_id: UUID) -> bool:
        """Deletes a comment by its ID."""
