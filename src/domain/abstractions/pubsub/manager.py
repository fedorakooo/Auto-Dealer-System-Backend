from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine


class IPubSubManager(ABC):
    """Interface for Publish/Subscribe messaging pattern."""

    @abstractmethod
    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        """Publish a message to a specific channel."""
        pass

    @abstractmethod
    async def subscribe(self, channel: str, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        """Subscribe to a specific channel and process incoming messages with the callback."""
        pass
