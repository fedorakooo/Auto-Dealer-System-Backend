from abc import ABC, abstractmethod
from typing import Any


class ITokenHandler(ABC):
    """Interface for handling token operations."""

    @abstractmethod
    def encode_jwt(
        self,
        payload: dict,
        expire_minutes: float,
    ) -> str:
        """Encodes the given payload into a JWT token."""
        pass

    @abstractmethod
    def decode_jwt(
        self,
        token: str | bytes,
    ) -> dict[str, Any]:
        """Decodes the given JWT and returns its payload."""
        pass

    @abstractmethod
    def get_token_type(
        self,
        token: str | bytes,
    ) -> str:
        """Gets the token type from the JWT payload."""
        pass
