from abc import ABC, abstractmethod


class AbstractPasswordHandler(ABC):
    """Abstract password handler interface."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password."""
        pass

    @abstractmethod
    def validate_password(self, password: str, hashed_password: str) -> bool:
        """Validate password against hash."""
        pass
