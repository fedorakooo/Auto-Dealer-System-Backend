from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.custom_order_dto import (
    CustomOrderCreateDTO,
    CustomOrderDTO,
    CustomOrderUpdateDTO,
)
from src.domain.value_objects.custom_order_status import CustomOrderStatus


class ICustomOrderService(ABC):
    """Interface for custom order operations."""

    @abstractmethod
    async def create_custom_order(self, create_dto: CustomOrderCreateDTO) -> CustomOrderDTO:
        """Create a new custom order."""
        pass

    @abstractmethod
    async def get_custom_order(self, custom_order_id: UUID) -> CustomOrderDTO:
        """Get custom order by ID."""
        pass

    @abstractmethod
    async def get_custom_orders_by_customer(self, customer_id: UUID) -> list[CustomOrderDTO]:
        """Get custom orders by customer ID."""
        pass

    @abstractmethod
    async def get_custom_orders_by_dealership(self, dealership_id: int) -> list[CustomOrderDTO]:
        """Get custom orders by dealership ID."""
        pass

    @abstractmethod
    async def update_custom_order(
        self,
        custom_order_id: UUID,
        update_dto: CustomOrderUpdateDTO,
        current_user_id: UUID | None = None,
    ) -> CustomOrderDTO:
        """Update custom order."""
        pass

    @abstractmethod
    async def update_custom_order_status(
        self,
        custom_order_id: UUID,
        new_status: CustomOrderStatus,
        current_user_id: UUID | None = None,
    ) -> CustomOrderDTO:
        """Update custom order status."""
        pass

    @abstractmethod
    async def delete_custom_order(
        self,
        custom_order_id: UUID,
        current_user_id: UUID | None = None,
    ) -> bool:
        """Delete custom order."""
        pass
