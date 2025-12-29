from abc import ABC, abstractmethod

from src.domain.entities.dealership import Dealership


class IDealershipRepository(ABC):
    """Interface for dealership repository operations."""

    @abstractmethod
    async def get_by_id(self, dealership_id: int) -> Dealership | None:
        """Returns one dealership by ID or None."""
        pass

    @abstractmethod
    async def get_all(self, page: int = 1, limit: int = 20) -> tuple[list[Dealership], int]:
        """Returns all dealerships with pagination."""
        pass

    @abstractmethod
    async def get_active(self) -> list[Dealership]:
        """Returns all active dealerships."""
        pass

    @abstractmethod
    async def get_by_city_id(self, city_id: int) -> list[Dealership]:
        """Returns dealerships by city ID."""
        pass

    @abstractmethod
    async def get_by_country(self, country: str) -> list[Dealership]:
        """Returns dealerships by country."""
        pass

    @abstractmethod
    async def create(self, dealership: Dealership) -> Dealership:
        """Creates a new dealership and returns the created dealership."""
        pass

    @abstractmethod
    async def update(self, dealership: Dealership) -> Dealership:
        """Updates a dealership and returns the updated dealership."""
        pass

    @abstractmethod
    async def delete(self, dealership_id: int) -> bool:
        """Deletes a dealership by its ID."""
        pass
