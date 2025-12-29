from abc import ABC, abstractmethod

from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)


class IDealershipService(ABC):
    """Interface for dealership operations."""

    @abstractmethod
    async def create_dealership(self, create_dto: DealershipCreateDTO) -> DealershipDTO:
        """Create a new dealership."""
        pass

    @abstractmethod
    async def get_dealership(self, dealership_id: int) -> DealershipDTO:
        """Get dealership by ID."""
        pass

    @abstractmethod
    async def get_all_dealerships(self, page: int = 1, limit: int = 20) -> tuple[list[DealershipDTO], int]:
        """Get all dealerships with pagination."""
        pass

    @abstractmethod
    async def get_active_dealerships(self) -> list[DealershipDTO]:
        """Get active dealerships."""
        pass

    @abstractmethod
    async def get_dealerships_by_city(self, city_id: int) -> list[DealershipDTO]:
        """Get dealerships by city ID."""
        pass

    @abstractmethod
    async def get_dealerships_by_country(self, country: str) -> list[DealershipDTO]:
        """Get dealerships by country."""
        pass

    @abstractmethod
    async def update_dealership(self, dealership_id: int, update_dto: DealershipUpdateDTO) -> DealershipDTO:
        """Update dealership."""
        pass

    @abstractmethod
    async def delete_dealership(self, dealership_id: int) -> bool:
        """Delete dealership."""
        pass
