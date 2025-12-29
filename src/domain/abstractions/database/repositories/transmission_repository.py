from abc import ABC, abstractmethod

from src.domain.entities.transmission import Transmission


class ITransmissionRepository(ABC):
    """Interface for transmission repository operations."""

    @abstractmethod
    async def get_by_id(self, transmission_id: int) -> Transmission | None:
        """Returns one transmission by ID or None."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Transmission]:
        """Returns all transmissions."""
        pass

    @abstractmethod
    async def create(self, transmission: Transmission) -> Transmission:
        """Creates a new transmission and returns the created transmission."""
        pass

    @abstractmethod
    async def update(self, transmission: Transmission) -> Transmission:
        """Updates a transmission and returns the updated transmission."""
        pass

    @abstractmethod
    async def delete(self, transmission_id: int) -> bool:
        """Deletes a transmission by its ID."""
        pass
