from typing import Annotated

from fastapi import Depends

from src.api.dependencies.database import get_unit_of_work
from src.api.dependencies.redis import get_redis_client, get_session_repository
from src.config import settings
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.abstractions.redis.session_repository import ISessionRepository
from src.domain.providers.current_user_provider import CurrentUserProvider
from src.infrastructure.auth.password_handler import PasswordHandler
from src.infrastructure.auth.token_handler import JWTTokenHandler


def get_password_handler() -> IPasswordHandler:
    return PasswordHandler()


def get_token_handler() -> ITokenHandler:
    return JWTTokenHandler(
        public_key=settings.jwt_settings.PUBLIC_KEY,
        private_key=settings.jwt_settings.PRIVATE_KEY,
        algorithm=settings.jwt_settings.algorithm,
    )


def get_current_user_provider(
    token_handler: Annotated[ITokenHandler, Depends(get_token_handler)],
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
    session_repository: Annotated[ISessionRepository, Depends(get_session_repository)],
) -> CurrentUserProvider:
    return CurrentUserProvider(
        token_handler=token_handler,
        uow=uow,
        redis_client=redis_client,
        session_repository=session_repository,
    )
