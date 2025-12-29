from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.domain.abstractions.auth.token_handler import ITokenHandler
from src.domain.exceptions.token_errors import InvalidTokenError as CustomInvalidTokenError
from src.domain.exceptions.token_errors import TokenExpiredError


class JWTTokenHandler(ITokenHandler):
    def __init__(self, public_key: str, private_key: str, algorithm: str):
        self.public_key = public_key
        self.private_key = private_key
        self.algorithm = algorithm

    def encode_jwt(
        self,
        payload: dict,
        expire_minutes: float,
    ) -> str:
        now = datetime.now(UTC)
        expire = now + timedelta(
            minutes=expire_minutes,
        )
        to_encode = {
            **payload,
            "exp": expire,
            "iat": now,
        }
        encoded = jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm,
        )
        return encoded

    def decode_jwt(
        self,
        token: str | bytes,
    ) -> dict[str, Any]:
        try:
            decoded = jwt.decode(
                jwt=token, key=self.public_key, algorithms=[self.algorithm], options={"verify_signature": True}
            )
        except ExpiredSignatureError as err:
            raise TokenExpiredError from err
        except InvalidTokenError as err:
            raise CustomInvalidTokenError from err
        return decoded

    def get_token_type(
        self,
        token: str | bytes,
    ) -> str:
        payload = self.decode_jwt(token)
        token_type = payload.get("token_type")
        if not token_type:
            raise CustomInvalidTokenError("Token type not found in payload")
        return token_type
