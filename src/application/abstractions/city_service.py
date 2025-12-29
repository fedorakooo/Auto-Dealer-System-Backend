from abc import ABC, abstractmethod

from src.application.dtos.city_dto import CityCreateDTO, CityDTO, CityUpdateDTO


class ICityService(ABC):
    """Interface for city operations."""

    @abstractmethod
    async def create_city(self, create_dto: CityCreateDTO) -> CityDTO:
        """Create a new city."""
        pass

    @abstractmethod
    async def get_city(self, city_id: int) -> CityDTO:
        """Get city by ID."""
        pass

    @abstractmethod
    async def get_all_cities(self) -> list[CityDTO]:
        """Get all cities."""
        pass

    @abstractmethod
    async def update_city(self, city_id: int, update_dto: CityUpdateDTO) -> CityDTO:
        """Update city."""
        pass

    @abstractmethod
    async def delete_city(self, city_id: int) -> bool:
        """Delete city."""
        pass
