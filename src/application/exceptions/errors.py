class ApplicationError(Exception):
    """Base exception for application layer errors."""

    pass


class NotFoundError(ApplicationError):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str | None = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message)


class ValidationError(ApplicationError):
    """Raised when validation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BusinessError(ApplicationError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PermissionError(ApplicationError):
    """Raised when user doesn't have permission to perform action."""

    def __init__(self, message: str = "Permission denied"):
        self.message = message
        super().__init__(message)
