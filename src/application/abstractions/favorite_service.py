from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.favorite_dto import FavoriteAddDTO, FavoriteRemoveDTO
from src.application.dtos.vehicle_dto import VehicleDTO


class IFavoriteService(ABC):
    """Interface for favorite operations."""

    @abstractmethod
    async def add_favorite(self, favorite_dto: FavoriteAddDTO) -> bool:
        """Add vehicle to favorites."""
        pass

    @abstractmethod
    async def remove_favorite(self, favorite_dto: FavoriteRemoveDTO) -> bool:
        """Remove vehicle from favorites."""
        pass

    @abstractmethod
    async def get_favorites(self, customer_id: UUID) -> list[VehicleDTO]:
        """Get favorite vehicles for customer."""
        pass
