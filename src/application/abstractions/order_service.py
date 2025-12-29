from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.order_dto import OrderCreateDTO, OrderDTO, OrderUpdateDTO
from src.domain.value_objects.filters import OrderFilter
from src.domain.value_objects.order_status import OrderStatus


class IOrderService(ABC):
    """Interface for order operations."""

    @abstractmethod
    async def create_order(self, create_dto: OrderCreateDTO) -> OrderDTO:
        """Create a new order."""
        pass

    @abstractmethod
    async def get_order(self, order_id: UUID) -> OrderDTO:
        """Get order by ID."""
        pass

    @abstractmethod
    async def get_orders(self, order_filter: OrderFilter) -> tuple[list[OrderDTO], int]:
        """Get orders with filtering and pagination."""
        pass

    @abstractmethod
    async def get_orders_by_customer(self, customer_id: UUID) -> list[OrderDTO]:
        """Get orders by customer ID."""
        pass

    @abstractmethod
    async def get_orders_by_dealership(self, dealership_id: int) -> list[OrderDTO]:
        """Get orders by dealership ID."""
        pass

    @abstractmethod
    async def update_order(
        self,
        order_id: UUID,
        update_dto: OrderUpdateDTO,
        current_user_id: UUID | None = None,
    ) -> OrderDTO:
        """Update order."""
        pass

    @abstractmethod
    async def update_order_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        current_user_id: UUID | None = None,
    ) -> OrderDTO:
        """Update order status."""
        pass

    @abstractmethod
    async def delete_order(self, order_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete order."""
        pass
