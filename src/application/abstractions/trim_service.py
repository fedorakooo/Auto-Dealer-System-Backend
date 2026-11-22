from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.trim_dto import TrimCreateDTO, TrimDTO, TrimUpdateDTO


class ITrimService(ABC):
    """Interface for trim operations."""

    @abstractmethod
    async def create_trim(self, create_dto: TrimCreateDTO) -> TrimDTO:
        """Create a trim of a model."""

    @abstractmethod
    async def get_trim(self, trim_id: UUID) -> TrimDTO:
        """Get trim by ID."""

    @abstractmethod
    async def get_trims_by_model(self, model_id: UUID) -> list[TrimDTO]:
        """Get all trims of a model."""

    @abstractmethod
    async def update_trim(self, trim_id: UUID, update_dto: TrimUpdateDTO) -> TrimDTO:
        """Update trim."""

    @abstractmethod
    async def delete_trim(self, trim_id: UUID) -> bool:
        """Delete trim; fails while vehicles or custom orders use it."""
