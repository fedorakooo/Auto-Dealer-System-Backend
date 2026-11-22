from abc import ABC, abstractmethod

from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)
from src.domain.entities.user import User


class IDealershipService(ABC):
    """Interface for dealership operations."""

    @abstractmethod
    async def create_dealership(self, create_dto: DealershipCreateDTO) -> DealershipDTO:
        """Create a new dealership."""

    @abstractmethod
    async def get_dealership(self, dealership_id: int) -> DealershipDTO:
        """Get dealership by ID."""

    @abstractmethod
    async def get_all_dealerships(self, page: int = 1, limit: int = 20) -> tuple[list[DealershipDTO], int]:
        """Get all dealerships with pagination."""

    @abstractmethod
    async def get_active_dealerships(self) -> list[DealershipDTO]:
        """Get active dealerships."""

    @abstractmethod
    async def get_dealerships_by_city(self, city_id: int) -> list[DealershipDTO]:
        """Get dealerships by city ID."""

    @abstractmethod
    async def get_dealerships_by_country(self, country: str) -> list[DealershipDTO]:
        """Get dealerships by country."""

    @abstractmethod
    async def get_managed_dealerships(self, requesting_user: User) -> list[DealershipDTO]:
        """Get dealerships the user may manage: all for an admin, the own one for an employee."""

    @abstractmethod
    async def update_dealership(
        self, dealership_id: int, update_dto: DealershipUpdateDTO, requesting_user: User
    ) -> DealershipDTO:
        """Update dealership; only an admin or an employee of this dealership may do it."""

    @abstractmethod
    async def delete_dealership(self, dealership_id: int) -> bool:
        """Delete dealership."""
