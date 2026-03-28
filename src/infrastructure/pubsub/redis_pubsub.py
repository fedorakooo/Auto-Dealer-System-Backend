import asyncio
import json
from typing import Any, Callable, Coroutine

import redis.asyncio as aioredis

from src.config import settings
from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.logger import get_logger

logger = get_logger(__name__)


class RedisPubSubManager(IPubSubManager):
    """Redis implementation of Pub/Sub manager."""

    def __init__(self) -> None:
        auth_str = f"{settings.redis_settings.username}:{settings.redis_settings.password}@" if settings.redis_settings.password else ""
        self._redis = aioredis.from_url(
            f"redis://{auth_str}{settings.redis_settings.host}:{settings.redis_settings.port}/1",
            decode_responses=True,
        )
        self._pubsub = self._redis.pubsub()
        self._callbacks: dict[str, list[Callable[[dict[str, Any]], Coroutine[Any, Any, None]]]] = {}
        self._listener_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        """Connect the pubsub client and start background listening."""
        logger.info("Initializing Redis PubSub connection...")
        try:
            await self._pubsub.ping()
            self._listener_task = asyncio.create_task(self._listen())
            logger.info("Redis PubSub connection established and listener started.")
        except Exception as e:
            logger.error(f"Failed to connect Redis PubSub: {e}")

    async def disconnect(self) -> None:
        """Close pubsub connection."""
        if self._listener_task:
            self._listener_task.cancel()
        await self._pubsub.close()
        await self._redis.aclose()
        logger.info("Redis PubSub disconnected")

    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        """Publish a JSON message to a Redis channel."""
        try:
            payload = json.dumps(message)
            await self._redis.publish(channel, payload)
            logger.debug(f"[PUBSUB] Published to {channel}: {payload}")
        except Exception as exc:
            logger.error(f"Failed to publish to {channel}: {exc}", exc_info=True)

    async def subscribe(self, channel: str, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        """Subscribe to a Redis channel with a callback function."""
        if channel not in self._callbacks:
            self._callbacks[channel] = []
            await self._pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")
            
        self._callbacks[channel].append(callback)

    async def _listen(self) -> None:
        """Background coroutine to iterate over pubsub messages."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    channel = str(message["channel"])
                    data_str = str(message["data"])
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message on {channel}: {data_str}")
                        continue
                        
                    callbacks = self._callbacks.get(channel, [])
                    for cb in callbacks:
                        try:
                            asyncio.create_task(cb(data))
                        except Exception as e:
                            logger.error(f"Error executing sub callback on {channel}: {e}", exc_info=True)
        except asyncio.CancelledError:
            logger.info("Redis PubSub listener task cancelled")
        except Exception as e:
            logger.error(f"Redis PubSub listen exception: {e}", exc_info=True)
