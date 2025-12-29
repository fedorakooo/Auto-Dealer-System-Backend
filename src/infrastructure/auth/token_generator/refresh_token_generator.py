from src.domain.abstractions.auth.token_generators.refresh_token_generator import (
    IRefreshTokenGenerator,
)
from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.entities.user import User
from src.domain.value_objects.auth_type import TokenType
from src.domain.value_objects.payload import RefreshTokenPayload


class RefreshTokenGenerator(IRefreshTokenGenerator):
    def __init__(
        self,
        token_handler: ITokenHandler,
        expire_minutes: float,
    ):
        self.token_handler = token_handler
        self.expire_minutes = expire_minutes

    def generate_refresh_token(self, user: User) -> str:
        payload = self._get_refresh_token_payload(user)
        return self.token_handler.encode_jwt(
            payload=dict(payload),
            expire_minutes=self.expire_minutes,
        )

    def _get_refresh_token_payload(self, user: User) -> RefreshTokenPayload:
        return RefreshTokenPayload(
            id=str(user.id),
            email=user.email,
            type=TokenType.REFRESH,
        )
