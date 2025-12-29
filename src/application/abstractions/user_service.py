from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.user_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from src.domain.value_objects.filters import UserFilter


class IUserService(ABC):
    """Interface for user operations."""

    @abstractmethod
    async def create_user(self, create_dto: UserCreateDTO) -> UserDTO:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user(self, user_id: UUID) -> UserDTO:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserDTO:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_users(self, user_filter: UserFilter) -> tuple[list[UserDTO], int]:
        """Get users with filtering and pagination."""
        pass

    @abstractmethod
    async def update_user(
        self,
        user_id: UUID,
        update_dto: UserUpdateDTO,
        current_user_id: UUID | None = None,
    ) -> UserDTO:
        """Update user."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete user."""
        pass
