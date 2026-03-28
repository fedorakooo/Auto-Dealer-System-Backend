from datetime import datetime, timedelta
from uuid import UUID, uuid4

from src.application.abstractions.auth_service import IAuthService
from src.application.dtos.auth_dto import LoginDTO, RefreshTokenDTO, TokenDTO
from src.application.exceptions.errors import NotFoundError, ValidationError
from src.config import settings
from src.domain.abstractions.auth.password_handler import IPasswordHandler
from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.abstractions.redis.session_repository import ISessionRepository
from src.domain.exceptions.auth_errors import InvalidCredentialsError
from src.domain.exceptions.token_errors import InvalidTokenError
from src.domain.exceptions.user_errors import UserBlockedError, UserInactiveError
from src.domain.value_objects.auth_type import TokenType
from src.domain.entities.session import UserSession
from src.logger import get_logger

logger = get_logger(__name__)


class AuthService(IAuthService):
    def __init__(
        self,
        uow: IUnitOfWork,
        password_handler: IPasswordHandler,
        token_handler: ITokenHandler,
        redis_client: IRedisClient,
        session_repository: ISessionRepository,
    ):
        self._uow = uow
        self._password_handler = password_handler
        self._token_handler = token_handler
        self._redis_client = redis_client
        self._session_repo = session_repository

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
        session_id = uuid4()
        expires_at = datetime.now() + timedelta(minutes=settings.jwt_settings.refresh_token_expire_minutes)
        session = UserSession(id=session_id, user_id=user.id, created_at=datetime.now(), expires_at=expires_at, is_active=True)
        await self._session_repo.save(session, default_ttl=int(settings.jwt_settings.refresh_token_expire_minutes * 60))

        access_token = self._token_handler.encode_jwt(
            payload={
                "id": str(user.id),
                "jti": str(session_id),
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
                "jti": str(session_id),
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

            jti = payload.get("jti")
            if not jti:
                raise InvalidTokenError("Token is missing session ID")
                
            session = await self._session_repo.get_by_id(UUID(jti))
            if not session or not session.is_active:
                logger.warning("Refresh token failed: session is invalid or expired")
                raise InvalidTokenError("Session is invalid or expired")

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
            # Invalidate old session
            await self._session_repo.delete(UUID(jti))

            new_session_id = uuid4()
            expires_at = datetime.now() + timedelta(minutes=settings.jwt_settings.refresh_token_expire_minutes)
            new_session = UserSession(id=new_session_id, user_id=user.id, created_at=datetime.now(), expires_at=expires_at, is_active=True)
            await self._session_repo.save(new_session, default_ttl=int(settings.jwt_settings.refresh_token_expire_minutes * 60))

            access_token = self._token_handler.encode_jwt(
                payload={
                    "id": str(user.id),
                    "jti": str(new_session_id),
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
                    "jti": str(new_session_id),
                    "email": user.email,
                    "token_type": TokenType.REFRESH,
                },
                expire_minutes=settings.jwt_settings.refresh_token_expire_minutes,
            )

            logger.info(f"Token refreshed successfully for user id: {user.id}")
            return TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except (NotFoundError, ValidationError, UserInactiveError, InvalidTokenError) as exc:
            logger.warning(f"Refresh token failed: {str(exc)}")
            raise ValidationError("Invalid refresh token") from exc

    async def logout(self, refresh_token: str) -> None:
        logger.debug("Processing logout request")
        try:
            payload = self._token_handler.decode_jwt(refresh_token)
            jti = payload.get("jti")
            if jti:
                await self._session_repo.delete(UUID(jti))
                logger.info(f"Logout successful, deleted session: {jti}")
        except Exception as exc:
            logger.warning(f"Logout failed (token might already be discarded): {exc}")

