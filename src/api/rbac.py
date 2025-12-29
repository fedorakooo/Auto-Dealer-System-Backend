from collections.abc import Callable
from functools import wraps
from typing import Any

from src.domain.entities.user import User
from src.domain.exceptions.auth_errors import ForbiddenError
from src.domain.value_objects.user_role import UserRole


class PermissionChecker:
    def __init__(self, roles: list[UserRole]):
        self.roles = roles

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            user: User | None = kwargs.get("requesting_user")
            if user is None:
                raise ForbiddenError()

            if user.role in self.roles:
                return await func(*args, **kwargs)
            else:
                raise ForbiddenError()

        return wrapper
