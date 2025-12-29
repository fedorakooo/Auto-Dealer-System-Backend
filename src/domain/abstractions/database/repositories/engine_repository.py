from abc import ABC, abstractmethod

from src.domain.entities.engine import Engine


class IEngineRepository(ABC):
    """Interface for engine repository operations."""

    @abstractmethod
    async def get_by_id(self, engine_id: int) -> Engine | None:
        """Returns one engine by ID or None."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Engine]:
        """Returns all engines."""
        pass

    @abstractmethod
    async def create(self, engine: Engine) -> Engine:
        """Creates a new engine and returns the created engine."""
        pass

    @abstractmethod
    async def update(self, engine: Engine) -> Engine:
        """Updates an engine and returns the updated engine."""
        pass

    @abstractmethod
    async def delete(self, engine_id: int) -> bool:
        """Deletes an engine by its ID."""
        pass
