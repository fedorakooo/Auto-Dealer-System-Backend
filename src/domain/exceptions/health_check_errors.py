class HealthCheckError(Exception):
    """Base exception for health check errors."""

    pass


class DatabaseHealthCheckError(HealthCheckError):
    """Raised when database health check fails."""

    def __init__(self, message: str = "Database health check failed"):
        super().__init__(message)


class RedisHealthCheckError(HealthCheckError):
    """Raised when Redis health check fails."""

    def __init__(self, message: str = "Redis health check failed"):
        super().__init__(message)


class MessageBrokerHealthCheckError(HealthCheckError):
    """Raised when message broker health check fails."""

    def __init__(self, message: str = "Message broker health check failed"):
        super().__init__(message)
