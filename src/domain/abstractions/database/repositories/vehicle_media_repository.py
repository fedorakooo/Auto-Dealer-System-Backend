from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.vehicle_media import VehicleMedia


class IVehicleMediaRepository(ABC):
    """Interface for vehicle media repository operations."""

    @abstractmethod
    async def get_by_id(self, media_id: UUID) -> VehicleMedia | None:
        """Returns one vehicle media by ID or None."""
        pass

    @abstractmethod
    async def get_by_vehicle_id(self, vehicle_id: UUID) -> list[VehicleMedia]:
        """Returns vehicle media by vehicle ID."""
        pass

    @abstractmethod
    async def create(self, vehicle_media: VehicleMedia) -> VehicleMedia:
        """Creates a new vehicle media and returns the created vehicle media."""
        pass

    @abstractmethod
    async def update(self, vehicle_media: VehicleMedia) -> VehicleMedia:
        """Updates a vehicle media and returns the updated vehicle media."""
        pass

    @abstractmethod
    async def delete(self, media_id: UUID) -> bool:
        """Deletes a vehicle media by its ID."""
        pass

    @abstractmethod
    async def delete_by_vehicle_id(self, vehicle_id: UUID) -> int:
        """Deletes all vehicle media by vehicle ID and returns the count of deleted items."""
        pass
