from abc import ABC, abstractmethod


class IDatabaseHealthCheck(ABC):
    """Interface for database health checks."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks database health status.

        Raises:
            DatabaseHealthCheckError: If database health check fails.
        """
        pass
