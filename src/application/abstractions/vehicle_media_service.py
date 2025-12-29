from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.vehicle_media_dto import (
    VehicleMediaCreateDTO,
    VehicleMediaDTO,
    VehicleMediaUpdateDTO,
)


class IVehicleMediaService(ABC):
    """Interface for vehicle media operations."""

    @abstractmethod
    async def create_vehicle_media(self, create_dto: VehicleMediaCreateDTO) -> VehicleMediaDTO:
        """Create a new vehicle media."""
        pass

    @abstractmethod
    async def get_vehicle_media(self, media_id: UUID) -> VehicleMediaDTO:
        """Get vehicle media by ID."""
        pass

    @abstractmethod
    async def get_media_by_vehicle(self, vehicle_id: UUID) -> list[VehicleMediaDTO]:
        """Get vehicle media by vehicle ID."""
        pass

    @abstractmethod
    async def update_vehicle_media(
        self,
        media_id: UUID,
        update_dto: VehicleMediaUpdateDTO,
    ) -> VehicleMediaDTO:
        """Update vehicle media."""
        pass

    @abstractmethod
    async def delete_vehicle_media(self, media_id: UUID) -> bool:
        """Delete vehicle media."""
        pass

    @abstractmethod
    async def delete_all_vehicle_media(self, vehicle_id: UUID) -> int:
        """Delete all media for a vehicle."""
        pass
