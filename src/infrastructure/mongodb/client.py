import asyncio
from functools import lru_cache
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)


class MongoDBClient:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db: Any = None

    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(settings.mongo_settings.url)
            self.db = self.client[settings.mongo_settings.MONGO_DB]

            # setup ttl index for the logs collection to delete old logs (90 days = 7776000 sec)
            await self.db.logs.create_index("timestamp", expireAfterSeconds=7776000)
            
            # Create indexes for faster search and filtering
            await self.db.logs.create_index("event_type")
            await self.db.logs.create_index("user_id")

            logger.info("MongoDB connected and indexes verified.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")


@lru_cache(maxsize=1)
def get_mongodb_client_singleton() -> MongoDBClient:
    return MongoDBClient()

