from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.vehicle import Vehicle


class IFavoriteRepository(ABC):
    """Interface for favorite repository operations."""

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[Vehicle]:
        """Returns favorite vehicles by customer ID."""
        pass

    @abstractmethod
    async def add(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        """Adds a vehicle to customer favorites."""
        pass

    @abstractmethod
    async def remove(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        """Removes a vehicle from customer favorites."""
        pass

    @abstractmethod
    async def exists(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        """Checks if a vehicle exists in customer favorites."""
        pass
