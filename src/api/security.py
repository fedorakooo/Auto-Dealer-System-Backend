from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from src.api.dependencies.auth import get_current_user_provider
from src.domain.entities.user import User
from src.domain.exceptions.token_errors import TokenError
from src.domain.exceptions.user_errors import UserBlockedError, UserNotFoundError
from src.domain.providers.current_user_provider import CurrentUserProvider

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/signin",
)


async def get_current_user(
    current_user_provider: Annotated[CurrentUserProvider, Depends(get_current_user_provider)],
    token: str = Depends(oauth2_scheme),
) -> User:
    """Resolves the authenticated user from the bearer token."""
    return await current_user_provider.get_current_user(token)


optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/signin",
    auto_error=False,
)


async def get_optional_current_user(
    current_user_provider: Annotated[CurrentUserProvider, Depends(get_current_user_provider)],
    token: str | None = Depends(optional_oauth2_scheme),
) -> User | None:
    """Current user for public endpoints that personalize output; anonymous or a stale token yields None."""
    if not token:
        return None
    try:
        return await current_user_provider.get_current_user(token)
    except (TokenError, UserBlockedError, UserNotFoundError):
        return None
