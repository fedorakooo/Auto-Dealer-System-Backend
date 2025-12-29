from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.review import Review


class IReviewRepository(ABC):
    """Interface for review repository operations."""

    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> Review | None:
        """Returns one review by ID or None."""
        pass

    @abstractmethod
    async def get_by_model_id(self, model_id: UUID) -> list[Review]:
        """Returns reviews by model ID."""
        pass

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[Review]:
        """Returns reviews by customer ID."""
        pass

    @abstractmethod
    async def create(self, review: Review) -> Review:
        """Creates a new review and returns the created review."""
        pass

    @abstractmethod
    async def update(self, review: Review) -> Review:
        """Updates a review and returns the updated review."""
        pass

    @abstractmethod
    async def delete(self, review_id: UUID) -> bool:
        """Deletes a review by its ID."""
        pass
