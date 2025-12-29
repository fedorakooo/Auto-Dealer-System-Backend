from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.review_dto import ReviewCreateDTO, ReviewDTO, ReviewUpdateDTO


class IReviewService(ABC):
    """Interface for review operations."""

    @abstractmethod
    async def create_review(self, create_dto: ReviewCreateDTO) -> ReviewDTO:
        """Create a new review."""
        pass

    @abstractmethod
    async def get_review(self, review_id: UUID) -> ReviewDTO:
        """Get review by ID."""
        pass

    @abstractmethod
    async def get_reviews_by_model(self, model_id: UUID) -> list[ReviewDTO]:
        """Get reviews by model ID."""
        pass

    @abstractmethod
    async def get_reviews_by_customer(self, customer_id: UUID) -> list[ReviewDTO]:
        """Get reviews by customer ID."""
        pass

    @abstractmethod
    async def update_review(
        self,
        review_id: UUID,
        update_dto: ReviewUpdateDTO,
        current_user_id: UUID | None = None,
    ) -> ReviewDTO:
        """Update review."""
        pass

    @abstractmethod
    async def delete_review(self, review_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete review."""
        pass
