class TokenError(Exception):
    """Base exception for token errors."""

    pass


class InvalidTokenError(TokenError):
    """Raised when token is invalid."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class TokenExpiredError(TokenError):
    """Raised when token is expired."""

    def __init__(self):
        super().__init__("Token has expired")


class TokenTypeError(TokenError):
    """Raised when token type is incorrect."""

    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Expected token type {expected}, got {actual}")
