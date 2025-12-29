from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from src.config import settings
from src.domain.abstractions.redis.healthcheck import IRedisHealthCheck
from src.domain.abstractions.redis.redis_client import IRedisClient
from src.infrastructure.redis.client import RedisClient
from src.infrastructure.redis.healthcheck import RedisHealthCheck
from src.logger import get_logger

logger = get_logger(__name__)


def get_redis() -> Redis:
    logger.debug(f"Creating Redis connection to {settings.redis_settings.host}:{settings.redis_settings.port}")
    return Redis(
        host=settings.redis_settings.host,
        port=settings.redis_settings.port,
        username=settings.redis_settings.username,
        password=settings.redis_settings.password,
        decode_responses=settings.redis_settings.decode_responses,
    )


def get_redis_client(request: Request) -> IRedisClient:
    redis_client: RedisClient | None = request.app.state.redis_client
    if redis_client is None:
        logger.error("Redis client is not initialized")
        raise RuntimeError("Redis client is not initialized")
    return redis_client


def get_redis_health_check(
    redis_client: Annotated[IRedisClient, Depends(get_redis_client)],
) -> IRedisHealthCheck:
    return RedisHealthCheck(redis_client)
