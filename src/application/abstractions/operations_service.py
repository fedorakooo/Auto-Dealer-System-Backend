from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class IOperationsService(ABC):
    """Interface for extended dealership operations."""

    @abstractmethod
    async def vehicle_history(self, vehicle_id: UUID, kind: str, limit: int) -> list[dict[str, Any]]:
        """Get price or lifecycle-status history for a vehicle."""
        pass

    @abstractmethod
    async def add_vehicle_status(
        self,
        vehicle_id: UUID,
        status: str,
        reason: str | None,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Add a vehicle lifecycle-status history entry."""
        pass

    @abstractmethod
    async def order_history(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        """Get status history for an order."""
        pass

    @abstractmethod
    async def payments(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        """Get payments for an order."""
        pass

    @abstractmethod
    async def create_payment(
        self,
        order_id: UUID,
        body: dict[str, Any],
        key: str,
        user_id: UUID,
    ) -> dict[str, Any]:
        """Register an idempotent payment for an order."""
        pass

    @abstractmethod
    async def addresses(self, user_id: UUID) -> list[dict[str, Any]]:
        """Get addresses for the current customer."""
        pass

    @abstractmethod
    async def create_address(self, user_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        """Create an address for the current customer."""
        pass

    @abstractmethod
    async def delete_address(self, user_id: UUID, address_id: UUID) -> None:
        """Delete one address belonging to the current customer."""
        pass

    @abstractmethod
    async def update_address(
        self,
        user_id: UUID,
        address_id: UUID,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update one address belonging to the current customer."""
        pass

    @abstractmethod
    async def employee_profiles(self, limit: int) -> list[dict[str, Any]]:
        """Get employee profiles."""
        pass

    @abstractmethod
    async def create_employee_profile(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create an employee profile."""
        pass

    @abstractmethod
    async def catalog(self, limit: int) -> list[dict[str, Any]]:
        """Get active service-catalog entries."""
        pass

    @abstractmethod
    async def create_appointment(
        self,
        user_id: UUID,
        body: dict[str, Any],
        key: str,
    ) -> dict[str, Any]:
        """Create an idempotent appointment for the current customer."""
        pass

    @abstractmethod
    async def appointments(self, user_id: UUID | None, limit: int) -> list[dict[str, Any]]:
        """Get appointments, optionally scoped to the current customer."""
        pass

    @abstractmethod
    async def change_appointment_status(self, appointment_id: UUID, status: str) -> dict[str, Any]:
        """Change and return an appointment status."""
        pass

    @abstractmethod
    async def delete_appointment(self, user_id: UUID, appointment_id: UUID) -> None:
        """Delete a requested appointment belonging to the current customer."""
        pass

    @abstractmethod
    async def create_service_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a service order."""
        pass

    @abstractmethod
    async def add_service_item(self, order_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        """Add an item to a service order."""
        pass

    @abstractmethod
    async def change_service_status(self, order_id: UUID, status: str) -> dict[str, Any]:
        """Change and return a service-order status."""
        pass

    @abstractmethod
    async def service_orders(self, limit: int) -> list[dict[str, Any]]:
        """Get service orders."""
        pass

    @abstractmethod
    async def spare_parts(self, limit: int) -> list[dict[str, Any]]:
        """Get active spare parts."""
        pass

    @abstractmethod
    async def inventory(self, dealership_id: int, below_reorder: bool, limit: int) -> list[dict[str, Any]]:
        """Get dealership inventory."""
        pass

    @abstractmethod
    async def reserve_part(self, dealership_id: int, part_id: UUID, quantity: int) -> dict[str, Any]:
        """Reserve available dealership inventory."""
        pass
