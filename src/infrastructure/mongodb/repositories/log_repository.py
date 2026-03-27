from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from src.domain.abstractions.database.repositories.log_repository import ILogRepository
from src.domain.entities.log import AuditLog


class LogRepository(ILogRepository):
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def create(self, log: AuditLog) -> str:
        document = log.model_dump(by_alias=True, exclude_none=True)
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)

    async def get_logs(self, filters: dict[str, Any], limit: int = 100, skip: int = 0) -> list[dict[str, Any]]:
        cursor = self._collection.find(filters).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        # Convert ObjectId to string
        for log in logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
        return logs
