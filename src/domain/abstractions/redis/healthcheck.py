from abc import ABC, abstractmethod


class IRedisHealthCheck(ABC):
    """Interface for redis health checks."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Checks redis health status."""
        pass
