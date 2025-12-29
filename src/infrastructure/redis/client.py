from redis.asyncio import Redis

from src.domain.abstractions.redis.redis_client import IRedisClient
from src.logger import get_logger

logger = get_logger(__name__)


class RedisClient(IRedisClient):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, value: str) -> bool:
        logger.debug(f"Redis SET operation: key={key}")
        result = await self.redis.set(key, value)
        return result

    async def get(self, key: str) -> str | None:
        logger.debug(f"Redis GET operation: key={key}")
        result = await self.redis.get(key)
        return result

    async def setex(self, key: str, time: int, value: str) -> bool:
        logger.debug(f"Redis SETEX operation: key={key}, time={time}")
        result = await self.redis.setex(key, time, value)
        return result

    async def exists(self, key: str) -> bool:
        logger.debug(f"Redis EXISTS operation: key={key}")
        result = await self.redis.exists(key) == 1
        return result

    async def delete(self, key: str) -> bool:
        logger.debug(f"Redis DELETE operation: key={key}")
        result = await self.redis.delete(key)
        return result
