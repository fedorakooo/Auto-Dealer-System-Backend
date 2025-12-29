from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.domain.value_objects.filters import VehicleFilter


class IVehicleService(ABC):
    """Interface for vehicle operations."""

    @abstractmethod
    async def create_vehicle(self, create_dto: VehicleCreateDTO) -> VehicleDTO:
        """Create a new vehicle."""
        pass

    @abstractmethod
    async def get_vehicle(self, vehicle_id: UUID) -> VehicleDTO:
        """Get vehicle by ID."""
        pass

    @abstractmethod
    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[VehicleDTO], int]:
        """Get vehicles with filtering and pagination."""
        pass

    @abstractmethod
    async def search_vehicles(
        self,
        model_name: str | None = None,
        body_type: str | None = None,
        fuel_type: str | None = None,
        transmission_type: str | None = None,
        min_price: float = 0,
        max_price: float = 99999999,
        dealership_id: int | None = None,
    ) -> list[VehicleDTO]:
        """Search vehicles by various criteria."""
        pass

    @abstractmethod
    async def get_vehicles_by_dealership(self, dealership_id: int) -> list[VehicleDTO]:
        """Get vehicles by dealership ID."""
        pass

    @abstractmethod
    async def update_vehicle(self, vehicle_id: UUID, update_dto: VehicleUpdateDTO) -> VehicleDTO:
        """Update vehicle."""
        pass

    @abstractmethod
    async def delete_vehicle(self, vehicle_id: UUID) -> bool:
        """Delete vehicle."""
        pass
