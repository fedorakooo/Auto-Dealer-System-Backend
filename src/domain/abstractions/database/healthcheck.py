from abc import ABC, abstractmethod


class AbstractDatabaseHealthCheck(ABC):
    """Abstract class defining the interface for database health checks."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks database health status.

        Raises:
            DatabaseHealthCheckError: If database health check fails.
        """
        pass
