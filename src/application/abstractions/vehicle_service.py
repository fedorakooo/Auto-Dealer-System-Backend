from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.domain.value_objects.filters import VehicleFilter


class IVehicleService(ABC):
    """Interface for vehicle operations; a vehicle is always addressed through its model."""

    @abstractmethod
    async def create_vehicle(self, model_id: UUID, create_dto: VehicleCreateDTO) -> VehicleDTO:
        """Create a vehicle of the model; its trim must belong to that model."""

    @abstractmethod
    async def ensure_vehicle_in_model(self, model_id: UUID, vehicle_id: UUID) -> None:
        """Raise NotFoundError unless the vehicle exists and belongs to the model."""

    @abstractmethod
    async def get_vehicle(self, model_id: UUID, vehicle_id: UUID) -> VehicleDTO:
        """Get a vehicle of the model."""

    @abstractmethod
    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[VehicleDTO], int]:
        """Get vehicles with filtering and pagination, within one model or across models."""

    @abstractmethod
    async def update_vehicle(
        self, model_id: UUID, vehicle_id: UUID, update_dto: VehicleUpdateDTO, current_user_id: UUID | None = None
    ) -> VehicleDTO:
        """Update a vehicle of the model; its trim can only change within the model."""

    @abstractmethod
    async def delete_vehicle(self, model_id: UUID, vehicle_id: UUID) -> bool:
        """Delete a vehicle of the model."""
