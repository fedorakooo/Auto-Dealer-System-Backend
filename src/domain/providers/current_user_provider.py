from uuid import UUID

from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.entities.user import User
from src.domain.exceptions.token_errors import InvalidTokenError, TokenTypeError
from src.domain.exceptions.user_errors import UserBlockedError, UserNotFoundError
from src.domain.value_objects.auth_type import TokenType
from src.logger import get_logger

logger = get_logger(__name__)


class CurrentUserProvider:
    """Provider for getting current user from token."""

    def __init__(
        self,
        token_handler: ITokenHandler,
        uow: IUnitOfWork,
    ) -> None:
        self.token_handler = token_handler
        self.uow = uow

    async def get_current_user(self, token: str) -> User:
        """Get current user from token.

        Process:
        1. Decode JWT token
        2. Verify token type is ACCESS
        3. Extract user id from payload
        4. Fetch user from database
        5. Verify user exists and is active
        6. Return user entity
        """
        logger.debug("Getting current user from token")
        try:
            payload = self.token_handler.decode_jwt(token)
        except Exception as exc:
            logger.warning(f"Failed to decode token: {str(exc)}")
            raise InvalidTokenError(f"Failed to decode token: {str(exc)}") from exc

        # Verify token type
        token_type_str = self.token_handler.get_token_type(token)
        token_type = TokenType(token_type_str)
        if token_type != TokenType.ACCESS:
            logger.warning(f"Invalid token type: expected {TokenType.ACCESS.value}, got {token_type.value}")
            raise TokenTypeError(
                expected=TokenType.ACCESS.value,
                actual=token_type.value,
            )

        # Extract user id from payload
        user_id_str = payload.get("id") or payload.get("user_id") or payload.get("sub")
        if not user_id_str:
            logger.warning("Token payload missing user id")
            raise InvalidTokenError("Token payload missing user id")

        try:
            user_id = UUID(str(user_id_str))
        except (ValueError, TypeError) as exc:
            logger.warning(f"Invalid user id in token: {str(exc)}")
            raise InvalidTokenError(f"Invalid user id in token: {str(exc)}") from exc

        # Fetch user from database
        logger.debug(f"Fetching user from database with id: {user_id}")
        async with self.uow:
            user = await self.uow.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found with id: {user_id}")
                raise UserNotFoundError(user_id=str(user_id))

            # Verify user is active (additional check for security)
            # Also check token payload if available
            token_is_active = payload.get("is_active")
            if token_is_active is not None and not token_is_active:
                logger.warning(f"User is blocked: {user.email}")
                raise UserBlockedError(email=user.email)

            # Verify user is still active in database
            if not user.is_active:
                logger.warning(f"User is inactive in database: {user.email}")
                raise UserBlockedError(email=user.email)

        logger.debug(f"Current user retrieved successfully: {user.email} (id: {user.id})")
        return user
