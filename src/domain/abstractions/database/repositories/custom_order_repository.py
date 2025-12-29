from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.custom_order import CustomOrder
from src.domain.value_objects.custom_order_status import CustomOrderStatus


class ICustomOrderRepository(ABC):
    """Interface for custom order repository operations."""

    @abstractmethod
    async def get_by_id(self, custom_order_id: UUID) -> CustomOrder | None:
        """Returns one custom order by ID or None."""
        pass

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[CustomOrder]:
        """Returns custom orders by customer ID."""
        pass

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[CustomOrder]:
        """Returns custom orders by dealership ID."""
        pass

    @abstractmethod
    async def create(self, custom_order: CustomOrder) -> CustomOrder:
        """Creates a new custom order and returns the created custom order."""
        pass

    @abstractmethod
    async def update(self, custom_order: CustomOrder) -> CustomOrder:
        """Updates a custom order and returns the updated custom order."""
        pass

    @abstractmethod
    async def update_status(self, custom_order_id: UUID, new_status: CustomOrderStatus) -> CustomOrder:
        """Updates custom order status and returns the updated custom order."""
        pass

    @abstractmethod
    async def delete(self, custom_order_id: UUID) -> bool:
        """Deletes a custom order by its ID."""
        pass
