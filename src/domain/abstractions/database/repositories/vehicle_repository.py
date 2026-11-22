from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.domain.entities.vehicle import Vehicle
from src.domain.value_objects.filters import VehicleFilter
from src.domain.value_objects.vehicle_status import VehicleStatus


class IVehicleRepository(ABC):
    """Interface for vehicle repository operations."""

    @abstractmethod
    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        """Returns one vehicle by ID or None."""

    @abstractmethod
    async def get_by_vin(self, vin: str) -> Vehicle | None:
        """Returns one vehicle by VIN or None."""

    @abstractmethod
    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[Vehicle], int]:
        """Returns vehicles based on filter."""

    @abstractmethod
    async def get_model_ids(self, vehicle_ids: list[UUID]) -> dict[UUID, UUID]:
        """Returns the model of each given vehicle; unknown vehicles are omitted."""

    @abstractmethod
    async def get_model_stock_stats(self, model_ids: list[UUID]) -> dict[UUID, tuple[int, Decimal | None]]:
        """Returns (in-stock count, lowest in-stock price) per model; models without stock are omitted."""

    @abstractmethod
    async def create(self, vehicle: Vehicle) -> Vehicle:
        """Creates a new vehicle and returns the created vehicle."""

    @abstractmethod
    async def update(self, vehicle: Vehicle) -> Vehicle:
        """Updates a vehicle and returns the updated vehicle."""

    @abstractmethod
    async def update_status(
        self, vehicle_id: UUID, status: VehicleStatus, changed_by: UUID | None = None, reason: str | None = None
    ) -> bool:
        """Changes the vehicle lifecycle status and records who did it."""

    @abstractmethod
    async def delete(self, vehicle_id: UUID) -> bool:
        """Deletes a vehicle by its ID."""
