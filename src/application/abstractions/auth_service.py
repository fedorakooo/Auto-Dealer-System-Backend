from abc import ABC, abstractmethod

from src.application.dtos.auth_dto import LoginDTO, RefreshTokenDTO, TokenDTO


class IAuthService(ABC):
    """Interface for authentication operations."""

    @abstractmethod
    async def login(self, login_dto: LoginDTO) -> TokenDTO:
        """Authenticate user and return tokens."""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_dto: RefreshTokenDTO) -> TokenDTO:
        """Refresh access token using refresh token."""
        pass

    @abstractmethod
    async def logout(self, refresh_token: str) -> None:
        """Invalidate the session associated with the refresh token."""
        pass
