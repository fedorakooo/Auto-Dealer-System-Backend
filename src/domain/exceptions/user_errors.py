class UserBlockedError(Exception):
    """Raised when user is blocked and cannot perform action."""

    def __init__(self, user_id: str | None = None, email: str | None = None):
        self.user_id = user_id
        self.email = email
        message = "User is blocked"
        if email:
            message = f"User with email {email} is blocked"
        elif user_id:
            message = f"User with id {user_id} is blocked"
        super().__init__(message)


class UserNotFoundError(Exception):
    """Raised when user is not found."""

    def __init__(self, user_id: str | None = None, email: str | None = None):
        self.user_id = user_id
        self.email = email
        message = "User not found"
        if email:
            message = f"User with email {email} not found"
        elif user_id:
            message = f"User with id {user_id} not found"
        super().__init__(message)


class UserInactiveError(Exception):
    """Raised when user is inactive."""

    def __init__(self, user_id: str | None = None, email: str | None = None):
        self.user_id = user_id
        self.email = email
        message = "User is inactive"
        if email:
            message = f"User with email {email} is inactive"
        elif user_id:
            message = f"User with id {user_id} is inactive"
        super().__init__(message)
