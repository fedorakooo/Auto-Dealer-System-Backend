from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.vehicle import Vehicle
from src.domain.value_objects.filters import VehicleFilter


class IVehicleRepository(ABC):
    """Interface for vehicle repository operations."""

    @abstractmethod
    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        """Returns one vehicle by ID or None."""
        pass

    @abstractmethod
    async def get_by_vin(self, vin: str) -> Vehicle | None:
        """Returns one vehicle by VIN or None."""
        pass

    @abstractmethod
    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[Vehicle], int]:
        """Returns vehicles based on filter."""
        pass

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[Vehicle]:
        """Returns vehicles by dealership ID."""
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
    ) -> list[Vehicle]:
        """Searches vehicles by various criteria."""
        pass

    @abstractmethod
    async def create(self, vehicle: Vehicle) -> Vehicle:
        """Creates a new vehicle and returns the created vehicle."""
        pass

    @abstractmethod
    async def update(self, vehicle: Vehicle) -> Vehicle:
        """Updates a vehicle and returns the updated vehicle."""
        pass

    @abstractmethod
    async def delete(self, vehicle_id: UUID) -> bool:
        """Deletes a vehicle by its ID."""
        pass
