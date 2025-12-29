from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.model_media import ModelMedia


class IModelMediaRepository(ABC):
    """Interface for model media repository operations."""

    @abstractmethod
    async def get_by_id(self, media_id: UUID) -> ModelMedia | None:
        """Returns one model media by ID or None."""
        pass

    @abstractmethod
    async def get_by_model_id(self, model_id: UUID) -> list[ModelMedia]:
        """Returns model media by model ID."""
        pass

    @abstractmethod
    async def create(self, model_media: ModelMedia) -> ModelMedia:
        """Creates a new model media and returns the created model media."""
        pass

    @abstractmethod
    async def update(self, model_media: ModelMedia) -> ModelMedia:
        """Updates a model media and returns the updated model media."""
        pass

    @abstractmethod
    async def delete(self, media_id: UUID) -> bool:
        """Deletes a model media by its ID."""
        pass

    @abstractmethod
    async def delete_by_model_id(self, model_id: UUID) -> int:
        """Deletes all model media by model ID and returns the count of deleted items."""
        pass
