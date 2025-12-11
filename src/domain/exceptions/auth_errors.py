class LoginError(Exception):
    """Base exception for login errors."""

    pass


class InvalidEmailError(LoginError):
    """Raised when email is invalid."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Invalid email: {email}")


class InvalidPasswordError(LoginError):
    """Raised when password is invalid."""

    def __init__(self):
        super().__init__("Invalid password")


class InvalidCredentialsError(LoginError):
    """Raised when credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid email or password")
