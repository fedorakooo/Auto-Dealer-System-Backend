from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.feature import Feature


class IFeatureRepository(ABC):
    """Interface for feature repository operations."""

    @abstractmethod
    async def get_by_id(self, feature_id: int) -> Feature | None:
        """Returns one feature by ID or None."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Feature]:
        """Returns all features."""
        pass

    @abstractmethod
    async def get_by_model_id(self, model_id: UUID) -> list[Feature]:
        """Returns features by model ID."""
        pass

    @abstractmethod
    async def get_by_custom_order_id(self, custom_order_id: UUID) -> list[Feature]:
        """Returns features by custom order ID."""
        pass

    @abstractmethod
    async def create(self, feature: Feature) -> Feature:
        """Creates a new feature and returns the created feature."""
        pass

    @abstractmethod
    async def update(self, feature: Feature) -> Feature:
        """Updates a feature and returns the updated feature."""
        pass

    @abstractmethod
    async def delete(self, feature_id: int) -> bool:
        """Deletes a feature by its ID."""
        pass

    @abstractmethod
    async def add_to_model(self, model_id: UUID, feature_id: int) -> bool:
        """Adds a feature to a model."""
        pass

    @abstractmethod
    async def remove_from_model(self, model_id: UUID, feature_id: int) -> bool:
        """Removes a feature from a model."""
        pass

    @abstractmethod
    async def add_to_custom_order(self, custom_order_id: UUID, feature_id: int) -> bool:
        """Adds a feature to a custom order."""
        pass

    @abstractmethod
    async def remove_from_custom_order(self, custom_order_id: UUID, feature_id: int) -> bool:
        """Removes a feature from a custom order."""
        pass
