class DatabaseError(Exception):
    """Base exception for all database errors."""

    def __init__(self, message: str = "Database error") -> None:
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to the database") -> None:
        super().__init__(message)


class DatabaseTransactionError(DatabaseError):
    """Exception raised when a database transaction fails."""

    def __init__(self, message: str = "Database transaction failed") -> None:
        super().__init__(message)


class DatabaseUniqueViolationError(DatabaseError):
    """Exception raised when an operation violates a unique constraint."""

    def __init__(self, field: str | None = None) -> None:
        message = "Unique constraint violation"
        if field:
            message = f"Unique constraint violation for field '{field}'"
        super().__init__(message)


class DatabaseForeignKeyViolationError(DatabaseError):
    """Exception raised when an operation violates a foreign key constraint."""

    def __init__(self) -> None:
        super().__init__("The operation couldn't be completed because it would violate data integrity")


class DatabaseNotFoundError(DatabaseError):
    """Exception raised when a requested database record is not found."""

    def __init__(self, entity: str | None = None) -> None:
        message = "Requested record was not found"
        if entity:
            message = f"{entity} was not found"
        super().__init__(message)


class UnitOfWorkNotStartedError(DatabaseTransactionError):
    """Exception raised when trying to access repositories before UnitOfWork context is started."""

    def __init__(self, message: str | None = None) -> None:
        default_message = "UnitOfWork is not started. Use 'async with uow:' context manager."
        super().__init__(message or default_message)
