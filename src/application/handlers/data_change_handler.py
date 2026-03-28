from typing import Any

from src.application.utils.cache_manager import CacheManager
from src.logger import get_logger

logger = get_logger(__name__)


class DataChangeCacheHandler:
    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    async def handle(self, message: dict[str, Any]) -> None:
        entity = message.get("entity", "unknown")
        action = message.get("action", "unknown")
        item_id = message.get("id", "none")
        logger.info(f"[SYNC EVENT] Cross-instance state update -> {action} on {entity} (ID: {item_id})")
        if entity == "user" and item_id != "none":
            await self._cache.invalidate_namespace("users")
            await self._cache.delete_cached(f"user:{item_id}")
            await self._cache.delete_cached(f"user:session:{item_id}")
