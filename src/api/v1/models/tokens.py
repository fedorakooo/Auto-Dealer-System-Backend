"""Pydantic models for token API."""

from pydantic import BaseModel

from src.application.dtos.auth_dto import TokenDTO, TokenInfoDTO
from src.domain.value_objects.auth_type import AuthType


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    auth_type: AuthType

    @classmethod
    def from_dto(cls, token_info: TokenDTO | TokenInfoDTO) -> "TokenResponse":
        if isinstance(token_info, TokenInfoDTO):
            return TokenResponse(
                access_token=token_info.access_token,
                refresh_token=token_info.refresh_token,
                auth_type=token_info.auth_type,
            )
        else:
            # TokenDTO - use BEARER as default auth type
            return TokenResponse(
                access_token=token_info.access_token,
                refresh_token=token_info.refresh_token,
                auth_type=AuthType.BEARER,
            )
