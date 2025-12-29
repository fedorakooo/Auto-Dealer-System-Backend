from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.customer import Customer


class ICustomerRepository(ABC):
    """Interface for customer repository operations."""

    @abstractmethod
    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        """Returns one customer by ID or None."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Customer | None:
        """Returns one customer by user ID or None."""
        pass

    @abstractmethod
    async def create(self, customer: Customer) -> Customer:
        """Creates a new customer and returns the created customer."""
        pass

    @abstractmethod
    async def update(self, customer: Customer) -> Customer:
        """Updates a customer and returns the updated customer."""
        pass

    @abstractmethod
    async def delete(self, customer_id: UUID) -> bool:
        """Deletes a customer by its ID."""
        pass
