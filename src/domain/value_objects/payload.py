from typing import TypedDict

from src.domain.value_objects.auth_type import TokenType


class AccessTokenPayload(TypedDict):
    id: str
    email: str
    role: str
    is_active: bool
    type: TokenType


class RefreshTokenPayload(TypedDict):
    id: str
    email: str
    type: TokenType


class PasswordResetTokenPayload(TypedDict):
    id: str
    type: TokenType
