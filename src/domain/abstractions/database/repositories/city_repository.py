from abc import ABC, abstractmethod

from src.domain.entities.city import City


class ICityRepository(ABC):
    """Interface for city repository operations."""

    @abstractmethod
    async def get_by_id(self, city_id: int) -> City | None:
        """Returns one city by ID or None."""
        pass

    @abstractmethod
    async def get_all(self) -> list[City]:
        """Returns all cities."""
        pass

    @abstractmethod
    async def get_by_name_and_country(self, name: str, country: str) -> City | None:
        """Returns one city by name and country or None."""
        pass

    @abstractmethod
    async def create(self, city: City) -> City:
        """Creates a new city and returns the created city."""
        pass

    @abstractmethod
    async def update(self, city: City) -> City:
        """Updates a city and returns the updated city."""
        pass

    @abstractmethod
    async def delete(self, city_id: int) -> bool:
        """Deletes a city by its ID."""
        pass
