from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from src.api.dependencies.auth import get_current_user_provider
from src.domain.entities.user import User
from src.domain.providers.current_user_provider import CurrentUserProvider

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/signin",
)


async def get_current_user(
    current_user_provider: Annotated[CurrentUserProvider, Depends(get_current_user_provider)],
    token: str = Depends(oauth2_scheme),
) -> User:
    return await current_user_provider.get_current_user(token)
