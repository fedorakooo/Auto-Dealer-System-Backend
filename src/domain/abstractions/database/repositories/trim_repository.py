from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.trim import Trim


class ITrimRepository(ABC):
    """Interface for trim repository operations."""

    @abstractmethod
    async def get_by_id(self, trim_id: UUID) -> Trim | None:
        """Returns one trim by ID or None."""

    @abstractmethod
    async def get_by_model_id(self, model_id: UUID) -> list[Trim]:
        """Returns all trims of a model."""

    @abstractmethod
    async def create(self, trim: Trim) -> Trim:
        """Creates a new trim and returns the created trim."""

    @abstractmethod
    async def update(self, trim: Trim) -> Trim:
        """Updates a trim and returns the updated trim."""

    @abstractmethod
    async def delete(self, trim_id: UUID) -> bool:
        """Deletes a trim by its ID; raises TrimInUseError if it is still referenced."""
