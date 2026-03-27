from typing import Any, TypeVar

from pydantic import TypeAdapter

from src.domain.abstractions.redis.redis_client import IRedisClient
from src.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheManager:
    """Helper class for serializing and deserializing data to/from Redis using Pydantic."""

    def __init__(self, redis_client: IRedisClient):
        self.redis = redis_client

    async def get_cached(self, key: str, type_hint: Any) -> Any:
        try:
            cached_data = await self.redis.get(key)
            if not cached_data:
                return None

            adapter = TypeAdapter(type_hint)
            result = adapter.validate_json(cached_data)
            logger.debug(f"[CACHE HIT] Key: {key}")
            return result
        except Exception as exc:
            logger.error(f"Failed to get cache for {key}: {exc}", exc_info=True)
            return None

    async def set_cached(self, key: str, value: Any, type_hint: Any, ttl: int = 3600) -> None:
        try:
            adapter = TypeAdapter(type_hint)
            json_data = adapter.dump_json(value)
            await self.redis.setex(key, ttl, json_data.decode("utf-8"))
            logger.debug(f"[CACHE SET] Key: {key}, TTL: {ttl}")
        except Exception as exc:
            logger.error(f"Failed to set cache for {key}: {exc}", exc_info=True)

    async def delete_cached(self, key: str) -> None:
        try:
            await self.redis.delete(key)
            logger.debug(f"[CACHE DELETE] Key: {key}")
        except Exception as exc:
            logger.error(f"Failed to delete cache for {key}: {exc}", exc_info=True)

    async def get_namespace_version(self, namespace: str) -> int:
        """Get current version for namespace invalidation pattern."""
        try:
            version_key = f"{namespace}:version"
            version = await self.redis.get(version_key)
            return int(version) if version else 1
        except Exception as exc:
            logger.error(f"Failed to get namespace version for {namespace}: {exc}")
            return 1

    async def invalidate_namespace(self, namespace: str) -> None:
        """Increment version to invalidate all keys tied to this namespace."""
        try:
            version_key = f"{namespace}:version"
            new_version = await self.redis.incr(version_key)
            logger.debug(f"[CACHE INVALIDATE] Namespace: {namespace}, New Version: {new_version}")
        except Exception as exc:
            logger.error(f"Failed to invalidate namespace {namespace}: {exc}", exc_info=True)
