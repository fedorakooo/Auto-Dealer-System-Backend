from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.model import Model
from src.domain.value_objects.filters import ModelFilter


class IModelRepository(ABC):
    """Interface for model repository operations."""

    @abstractmethod
    async def get_by_id(self, model_id: UUID) -> Model | None:
        """Returns one model by ID or None."""
        pass

    @abstractmethod
    async def get_models(self, model_filter: ModelFilter) -> tuple[list[Model], int]:
        """Returns models based on filter."""
        pass

    @abstractmethod
    async def get_active_by_body_type(
        self, body_type_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Model], int]:
        """Returns active models by body type with pagination."""
        pass

    @abstractmethod
    async def get_active_by_production_year_range(
        self, year_start: int, year_end: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Model], int]:
        """Returns active models by production year range with pagination."""
        pass

    @abstractmethod
    async def create(self, model: Model) -> Model:
        """Creates a new model and returns the created model."""
        pass

    @abstractmethod
    async def update(self, model: Model) -> Model:
        """Updates a model and returns the updated model."""
        pass

    @abstractmethod
    async def delete(self, model_id: UUID) -> bool:
        """Deletes a model by its ID."""
        pass
