from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)


class IModelMediaService(ABC):
    """Interface for model media operations."""

    @abstractmethod
    async def create_model_media(self, create_dto: ModelMediaCreateDTO) -> ModelMediaDTO:
        """Create a new model media."""
        pass

    @abstractmethod
    async def get_model_media(self, media_id: UUID) -> ModelMediaDTO:
        """Get model media by ID."""
        pass

    @abstractmethod
    async def get_media_by_model(self, model_id: UUID) -> list[ModelMediaDTO]:
        """Get model media by model ID."""
        pass

    @abstractmethod
    async def update_model_media(
        self,
        media_id: UUID,
        update_dto: ModelMediaUpdateDTO,
    ) -> ModelMediaDTO:
        """Update model media."""
        pass

    @abstractmethod
    async def delete_model_media(self, media_id: UUID) -> bool:
        """Delete model media."""
        pass

    @abstractmethod
    async def delete_all_model_media(self, model_id: UUID) -> int:
        """Delete all media for a model."""
        pass
