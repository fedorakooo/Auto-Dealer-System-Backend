from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


class IOperationsRepository(ABC):
    """Interface for extended dealership operations persistence."""

    @abstractmethod
    async def vehicle_history(self, vehicle_id: UUID, kind: str, limit: int) -> list[dict[str, Any]]:
        """Returns the requested price or lifecycle-status history for a vehicle."""

    @abstractmethod
    async def add_vehicle_status(
        self,
        vehicle_id: UUID,
        status: str,
        reason: str | None,
        user_id: UUID,
    ) -> dict[str, Any] | None:
        """Changes the vehicle status and returns the history entry written by the trigger, None if no such vehicle."""

    @abstractmethod
    async def order_history(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        """Returns status history for an order."""

    @abstractmethod
    async def payments(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        """Returns payments registered for an order."""

    @abstractmethod
    async def create_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        method: str,
        status: str,
        external_reference: str | None,
    ) -> dict[str, Any]:
        """Creates and returns an order payment."""

    @abstractmethod
    async def addresses(self, customer_id: UUID) -> list[dict[str, Any]]:
        """Returns addresses belonging to a customer."""

    @abstractmethod
    async def create_address(self, customer_id: UUID, values: dict[str, Any]) -> dict[str, Any]:
        """Creates and returns a customer address."""

    @abstractmethod
    async def update_address(
        self,
        customer_id: UUID,
        address_id: UUID,
        values: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Updates a customer address and returns it when it exists."""

    @abstractmethod
    async def delete_address(self, customer_id: UUID, address_id: UUID) -> bool:
        """Deletes a customer address and reports whether it existed."""

    @abstractmethod
    async def employee_profiles(self, limit: int) -> list[dict[str, Any]]:
        """Returns employee profiles ordered by creation time."""

    @abstractmethod
    async def create_employee_profile(self, values: dict[str, Any]) -> dict[str, Any]:
        """Creates and returns an employee profile."""

    @abstractmethod
    async def service_catalog(self, limit: int) -> list[dict[str, Any]]:
        """Returns active service-catalog entries."""

    @abstractmethod
    async def create_appointment(
        self,
        customer_id: UUID,
        dealership_id: int,
        vehicle_id: UUID | None,
        requested_datetime: datetime,
        notes: str | None,
    ) -> dict[str, Any]:
        """Creates and returns a service appointment."""

    @abstractmethod
    async def appointments(self, customer_id: UUID | None, limit: int) -> list[dict[str, Any]]:
        """Returns appointments, optionally limited to one customer."""

    @abstractmethod
    async def change_appointment_status(self, appointment_id: UUID, status: str) -> dict[str, Any] | None:
        """Updates an appointment status and returns it when it exists."""

    @abstractmethod
    async def delete_appointment(self, appointment_id: UUID, customer_id: UUID) -> bool:
        """Deletes a requested appointment owned by the customer."""

    @abstractmethod
    async def create_service_order(self, values: dict[str, Any]) -> dict[str, Any]:
        """Creates and returns a service order."""

    @abstractmethod
    async def add_service_item(self, service_order_id: UUID, values: dict[str, Any]) -> dict[str, Any]:
        """Adds and returns an item for a service order."""

    @abstractmethod
    async def change_service_order_status(self, service_order_id: UUID, status: str) -> dict[str, Any]:
        """Changes and returns a service order status."""

    @abstractmethod
    async def service_orders(self, limit: int) -> list[dict[str, Any]]:
        """Returns service orders ordered by opening time."""

    @abstractmethod
    async def spare_parts(self, limit: int) -> list[dict[str, Any]]:
        """Returns active spare parts."""

    @abstractmethod
    async def inventory(self, dealership_id: int, below_reorder: bool, limit: int) -> list[dict[str, Any]]:
        """Returns inventory for a dealership."""

    @abstractmethod
    async def reserve_part(self, dealership_id: int, part_id: UUID, quantity: int) -> dict[str, Any]:
        """Reserves available inventory and returns the resulting balance."""

    @abstractmethod
    async def idempotency(self, key: str) -> dict[str, Any] | None:
        """Locks and returns an active idempotency result for a key."""

    @abstractmethod
    async def save_idempotency(
        self,
        key: str,
        user_id: UUID,
        method: str,
        path: str,
        request_hash: str,
        response_status: int,
        response_body: dict[str, Any],
    ) -> None:
        """Stores an idempotent response for a completed mutation."""

    @abstractmethod
    async def add_outbox(
        self,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Queues an event in the transactional outbox."""
