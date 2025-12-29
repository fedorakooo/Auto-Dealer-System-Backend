from dataclasses import dataclass

from src.domain.value_objects.auth_type import AuthType


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class TokenDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class TokenInfoDTO:
    access_token: str
    refresh_token: str
    auth_type: AuthType


@dataclass
class RefreshTokenDTO:
    refresh_token: str
