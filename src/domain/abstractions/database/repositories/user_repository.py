from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User
from src.domain.value_objects.filters import UserFilter


class AbstractUserRepository(ABC):
    """Abstract class defining the interface for user repository operations."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Returns one user by ID or None."""
        pass

    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> User | None:
        """Returns one user by phone number or None."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Returns one user by email or None."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Returns one user by username or None."""
        pass

    @abstractmethod
    async def get_users(self, user_filter: UserFilter) -> tuple[list[User], int]:
        """Returns users based on filter."""
        pass

    @abstractmethod
    async def get_users_by_group_id(
        self,
        user_filter: UserFilter,
        group_id: int,
    ) -> tuple[list[User], int]:
        """Returns users based on filter and group_id."""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Creates a new user and returns the created user."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Updates a user and returns the updated user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Deletes a user by its ID."""
        pass
