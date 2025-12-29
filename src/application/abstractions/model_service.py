from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.domain.value_objects.filters import ModelFilter


class IModelService(ABC):
    """Interface for model operations."""

    @abstractmethod
    async def create_model(self, create_dto: ModelCreateDTO) -> ModelDTO:
        """Create a new model."""
        pass

    @abstractmethod
    async def get_model(self, model_id: UUID) -> ModelDTO:
        """Get model by ID."""
        pass

    @abstractmethod
    async def get_models(self, model_filter: ModelFilter) -> tuple[list[ModelDTO], int]:
        """Get models with filtering and pagination."""
        pass

    @abstractmethod
    async def update_model(self, model_id: UUID, update_dto: ModelUpdateDTO) -> ModelDTO:
        """Update model."""
        pass

    @abstractmethod
    async def delete_model(self, model_id: UUID) -> bool:
        """Delete model."""
        pass
