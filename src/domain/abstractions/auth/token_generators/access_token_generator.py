from abc import ABC, abstractmethod

from src.domain.entities.user import User


class IAccessTokenGenerator(ABC):
    """Interface for generating an access tokens."""

    @abstractmethod
    def generate_access_token(self, user: User) -> str:
        """Generate a new access token."""
        pass
