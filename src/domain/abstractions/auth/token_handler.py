from abc import ABC, abstractmethod
from typing import Any

from src.domain.value_objects.token_type import TokenType


class AbstractTokenHandler(ABC):
    """Abstract token handler interface."""

    @abstractmethod
    def encode_jwt(self, payload: dict[str, Any], token_type: TokenType) -> str:
        """Encode JWT token."""
        pass

    @abstractmethod
    def decode_jwt(self, token: str) -> dict[str, Any]:
        """Decode JWT token."""
        pass

    @abstractmethod
    def get_token_type(self, token: str) -> TokenType:
        """Get token type from token."""
        pass
