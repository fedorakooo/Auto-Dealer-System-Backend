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
        pass

    @abstractmethod
    async def get_orders(self, order_filter: OrderFilter) -> tuple[list[Order], int]:
        """Returns orders based on filter."""
        pass

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[Order]:
        """Returns orders by customer ID."""
        pass

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[Order]:
        """Returns orders by dealership ID."""
        pass

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Creates a new order and returns the created order."""
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Updates an order and returns the updated order."""
        pass

    @abstractmethod
    async def update_status(self, order_id: UUID, new_status: OrderStatus) -> bool:
        """Updates order status by order ID."""
        pass

    @abstractmethod
    async def validate_status_transition(self, old_status: OrderStatus, new_status: OrderStatus) -> bool:
        """Validates if status transition is allowed using is_valid_status_transition function."""
        pass

    @abstractmethod
    async def delete(self, order_id: UUID) -> bool:
        """Deletes an order by its ID."""
        pass
