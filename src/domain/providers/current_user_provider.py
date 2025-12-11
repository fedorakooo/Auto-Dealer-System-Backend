from uuid import UUID

from src.domain.abstractions.auth.token_handler import AbstractTokenHandler, TokenType
from src.domain.abstractions.database.uow import AbstractUnitOfWork
from src.domain.entities.user import User
from src.domain.exceptions.token_errors import InvalidTokenError, TokenTypeError
from src.domain.exceptions.user_errors import UserBlockedError, UserNotFoundError


class CurrentUserProvider:
    """Provider for getting current user from token."""

    def __init__(
        self,
        token_handler: AbstractTokenHandler,
        uow: AbstractUnitOfWork,
    ) -> None:
        self.token_handler = token_handler
        self.uow = uow

    async def get_current_user(self, token: str) -> User:
        """Get current user from token."""
        try:
            payload = self.token_handler.decode_jwt(token)
        except Exception as exc:
            raise InvalidTokenError(f"Failed to decode token: {str(exc)}") from exc

        token_type = self.token_handler.get_token_type(token)
        if token_type != TokenType.ACCESS:
            raise TokenTypeError(
                expected=TokenType.ACCESS.value,
                actual=token_type.value,
            )

        user_id_str = payload.get("id") or payload.get("user_id")
        if not user_id_str:
            raise InvalidTokenError("Token payload missing user id")

        try:
            user_id = UUID(str(user_id_str))
        except (ValueError, TypeError) as e:
            raise InvalidTokenError(f"Invalid user id in token: {str(e)}") from e

        async with self.uow:
            user = await self.uow.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(user_id=str(user_id))

            if not user.is_active:
                raise UserBlockedError(email=user.email)

        return user
