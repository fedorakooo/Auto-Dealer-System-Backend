from datetime import datetime
from uuid import UUID

from src.application.abstractions.auth_service import IAuthService
from src.application.dtos.auth_dto import LoginDTO, RefreshTokenDTO, TokenDTO
from src.application.exceptions.errors import NotFoundError, ValidationError
from src.config import settings
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.exceptions.auth_errors import InvalidCredentialsError
from src.domain.exceptions.token_errors import InvalidTokenError
from src.domain.exceptions.user_errors import UserBlockedError, UserInactiveError
from src.domain.value_objects.auth_type import TokenType
from src.logger import get_logger

logger = get_logger(__name__)


class AuthService(IAuthService):
    def __init__(
        self,
        uow: IUnitOfWork,
        password_handler: IPasswordHandler,
        token_handler: ITokenHandler,
        redis_client: IRedisClient,
    ):
        self._uow = uow
        self._password_handler = password_handler
        self._token_handler = token_handler
        self._redis_client = redis_client

    async def login(self, login_dto: LoginDTO) -> TokenDTO:
        logger.debug(f"Processing login for email: {login_dto.email}")

        blacklist_key = f"auth:blacklist:{login_dto.email}"
        attempts_key = f"auth:attempts:{login_dto.email}"

        if await self._redis_client.exists(blacklist_key):
            logger.warning(f"Login failed: user blocked due to too many failed attempts: {login_dto.email}")
            raise UserBlockedError(email=login_dto.email)

        async with self._uow as uow:
            user = await uow.user_repository.get_by_email(login_dto.email)

            is_valid_password = False
            if user:
                is_valid_password = self._password_handler.validate_password(login_dto.password, user.hashed_password)

            if not user or not is_valid_password:
                logger.warning(f"Login failed: invalid credentials for email: {login_dto.email}")
                attempts = await self._redis_client.incr(attempts_key)
                if attempts == 1:
                    await self._redis_client.expire(attempts_key, 600)

                if attempts >= 3:
                    logger.warning(f"User {login_dto.email} exceeded login attempts. Blacklisting for 10 minutes.")
                    await self._redis_client.setex(blacklist_key, 600, "1")
                    await self._redis_client.delete(attempts_key)

                raise InvalidCredentialsError()

            if not user.is_active:
                logger.warning(f"Login failed: user inactive for email: {login_dto.email}")
                raise UserInactiveError(email=login_dto.email)

        await self._redis_client.delete(attempts_key)

        logger.debug(f"Generating tokens for user id: {user.id}")
        access_token = self._token_handler.encode_jwt(
            payload={
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "token_type": TokenType.ACCESS,
            },
            expire_minutes=settings.jwt_settings.access_token_expire_minutes,
        )
        refresh_token = self._token_handler.encode_jwt(
            payload={
                "id": str(user.id),
                "email": user.email,
                "token_type": TokenType.REFRESH,
            },
            expire_minutes=settings.jwt_settings.refresh_token_expire_minutes,
        )
        logger.info(f"Login successful for user id: {user.id}, email: {user.email}")
        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_token(self, refresh_dto: RefreshTokenDTO) -> TokenDTO:
        logger.debug("Processing refresh token request")
        try:
            payload = self._token_handler.decode_jwt(refresh_dto.refresh_token)
            token_type_str = self._token_handler.get_token_type(refresh_dto.refresh_token)
            token_type = TokenType(token_type_str)

            if token_type != TokenType.REFRESH:
                logger.warning("Refresh token failed: invalid token type")
                raise ValidationError("Invalid token type")

            blacklist_key = f"refresh-key:{refresh_dto.refresh_token}"
            if await self._redis_client.exists(blacklist_key):
                logger.warning("Refresh token failed: token is blacklisted")
                raise InvalidTokenError("Refresh token has been invalidated")

            user_id = UUID(payload.get("id") or payload.get("sub"))
            logger.debug(f"Refresh token for user id: {user_id}")
            async with self._uow as uow:
                user = await uow.user_repository.get_by_id(user_id)

                if not user:
                    logger.warning(f"Refresh token failed: user not found, id: {user_id}")
                    raise NotFoundError("User", str(user_id))

                if not user.is_active:
                    logger.warning(f"Refresh token failed: user inactive, id: {user_id}")
                    raise UserInactiveError(user_id=str(user_id))

            logger.debug(f"Generating new tokens for user id: {user.id}")
            access_token = self._token_handler.encode_jwt(
                payload={
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "token_type": TokenType.ACCESS,
                },
                expire_minutes=settings.jwt_settings.access_token_expire_minutes,
            )
            refresh_token = self._token_handler.encode_jwt(
                payload={
                    "id": str(user.id),
                    "email": user.email,
                    "token_type": TokenType.REFRESH,
                },
                expire_minutes=settings.jwt_settings.refresh_token_expire_minutes,
            )

            expiration_time = payload.get("exp")
            if expiration_time is not None:
                current_time = datetime.now().timestamp()
                ttl_seconds = int(expiration_time - current_time)
                if ttl_seconds > 0:
                    await self._redis_client.setex(
                        key=blacklist_key,
                        time=ttl_seconds,
                        value=refresh_dto.refresh_token,
                    )
                    logger.debug(f"Added refresh token to blacklist with TTL: {ttl_seconds} seconds")

            logger.info(f"Token refreshed successfully for user id: {user.id}")
            return TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except (NotFoundError, ValidationError, UserInactiveError, InvalidTokenError) as exc:
            logger.warning(f"Refresh token failed: {str(exc)}")
            raise ValidationError("Invalid refresh token") from exc
