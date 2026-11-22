from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.dealership import Dealership


class IDealershipRepository(ABC):
    """Interface for dealership repository operations."""

    @abstractmethod
    async def get_by_id(self, dealership_id: int) -> Dealership | None:
        """Returns one dealership by ID or None."""

    @abstractmethod
    async def get_all(self, page: int = 1, limit: int = 20) -> tuple[list[Dealership], int]:
        """Returns all dealerships with pagination."""

    @abstractmethod
    async def get_active(self) -> list[Dealership]:
        """Returns all active dealerships."""

    @abstractmethod
    async def get_by_city_id(self, city_id: int) -> list[Dealership]:
        """Returns dealerships by city ID."""

    @abstractmethod
    async def get_by_country(self, country: str) -> list[Dealership]:
        """Returns dealerships by country."""

    @abstractmethod
    async def create(self, dealership: Dealership) -> Dealership:
        """Creates a new dealership and returns the created dealership."""

    @abstractmethod
    async def update(self, dealership: Dealership) -> Dealership:
        """Updates a dealership and returns the updated dealership."""

    @abstractmethod
    async def delete(self, dealership_id: int) -> bool:
        """Deletes a dealership by its ID."""

    @abstractmethod
    async def get_employee_dealership_id(self, user_id: UUID) -> int | None:
        """Returns the dealership of an active employee profile, or None when the user has none."""
