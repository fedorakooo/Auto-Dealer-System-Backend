from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.order import Order
from src.domain.value_objects.filters import OrderFilter
from src.domain.value_objects.order_status import OrderStatus


class IOrderRepository(ABC):
    """Interface for order repository operations."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Returns one order by ID or None."""

    @abstractmethod
    async def get_orders(self, order_filter: OrderFilter) -> tuple[list[Order], int]:
        """Returns orders based on filter."""

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[Order]:
        """Returns orders by customer ID."""

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[Order]:
        """Returns orders by dealership ID."""

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Creates a new order; raises VehicleAlreadyOrderedError if the vehicle has an active order."""

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Updates an order and returns the updated order."""

    @abstractmethod
    async def update_status(self, order_id: UUID, new_status: OrderStatus, changed_by: UUID | None = None) -> bool:
        """Updates order status by order ID and records who did it."""

    @abstractmethod
    async def validate_status_transition(self, old_status: OrderStatus, new_status: OrderStatus) -> bool:
        """Validates if status transition is allowed using is_valid_status_transition function."""

    @abstractmethod
    async def delete(self, order_id: UUID) -> bool:
        """Deletes an order by its ID."""
