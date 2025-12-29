from src.domain.abstractions.redis.healthcheck import IRedisHealthCheck
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.exceptions.health_check_errors import RedisHealthCheckError


class RedisHealthCheck(IRedisHealthCheck):
    def __init__(self, redis_client: IRedisClient):
        self.redis_client = redis_client

    async def check_health(self) -> bool:
        try:
            await self.redis_client.exists("key")
            return True
        except Exception as exc:
            raise RedisHealthCheckError(f"Redis health check failed: {exc}") from exc
