from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.session import UserSession


class ISessionRepository(ABC):
    """Interface for managing active user sessions."""

    @abstractmethod
    async def save(self, session: UserSession, default_ttl: int = 3600) -> None:
        """Save a new user session or update an existing one."""
        pass

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[UserSession]:
        """Retrieve a session by its unique ID."""
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete an active session (e.g., on logout)."""
        pass
