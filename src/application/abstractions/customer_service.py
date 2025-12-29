from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.customer_dto import CustomerCreateDTO, CustomerDTO, CustomerUpdateDTO


class ICustomerService(ABC):
    """Interface for customer operations."""

    @abstractmethod
    async def create_customer(self, create_dto: CustomerCreateDTO) -> CustomerDTO:
        """Create a new customer."""
        pass

    @abstractmethod
    async def get_customer(self, customer_id: UUID) -> CustomerDTO:
        """Get customer by ID."""
        pass

    @abstractmethod
    async def get_customer_by_user_id(self, user_id: UUID) -> CustomerDTO:
        """Get customer by user ID."""
        pass

    @abstractmethod
    async def update_customer(self, customer_id: UUID, update_dto: CustomerUpdateDTO) -> CustomerDTO:
        """Update customer."""
        pass

    @abstractmethod
    async def delete_customer(self, customer_id: UUID) -> bool:
        """Delete customer."""
        pass
