from datetime import datetime
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

    async def get_activity_stats(self, period: str) -> list[dict[str, Any]]:
        format_str = "%Y-%m-%d"
        if period == "week":
            format_str = "%Y-%U"
        elif period == "month":
            format_str = "%Y-%m"

        pipeline = [
            {"$match": {"event_type": "USER_ACTION"}},
            {"$group": {
                "_id": {"$dateToString": {"format": format_str, "date": "$timestamp"}},
                "operations_count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$project": {
                "period": "$_id",
                "operations_count": 1,
                "unique_users_count": {"$size": "$unique_users"},
                "_id": 0
            }},
            {"$sort": {"period": 1}}
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        pipeline = [
            {"$match": {"event_type": "USER_ACTION", "user_id": {"$ne": None}}},
            {"$group": {"_id": "$user_id", "actions_count": {"$sum": 1}}},
            {"$sort": {"actions_count": -1}},
            {"$limit": limit},
            {"$project": {"user_id": "$_id", "actions_count": 1, "_id": 0}}
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_crud_stats(self) -> list[dict[str, Any]]:
        pipeline = [
            {"$match": {"event_type": "USER_ACTION"}},
            {"$project": {
                "operation_type": {
                    "$cond": {
                        "if": {"$regexMatch": {"input": "$action", "regex": "^CREATE"}}, "then": "CREATE",
                        "else": {"$cond": {
                            "if": {"$regexMatch": {"input": "$action", "regex": "^UPDATE"}}, "then": "UPDATE",
                            "else": {"$cond": {
                                "if": {"$regexMatch": {"input": "$action", "regex": "^DELETE"}}, "then": "DELETE",
                                "else": "READ/OTHER"
                            }}
                        }}
                    }
                }
            }},
            {"$group": {"_id": "$operation_type", "count": {"$sum": 1}}},
            {"$project": {"operation_type": "$_id", "count": 1, "_id": 0}}
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_time_series(self, start_time: datetime, end_time: datetime, interval: str) -> list[dict[str, Any]]:
        format_str = "%Y-%m-%dT%H:00:00Z"
        if interval == "day":
            format_str = "%Y-%m-%d"
        elif interval == "minute":
            format_str = "%Y-%m-%dT%H:%M:00Z"

        pipeline = [
            {"$match": {
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }},
            {"$group": {
                "_id": {
                    "time_bucket": {"$dateToString": {"format": format_str, "date": "$timestamp"}},
                    "event_type": "$event_type"
                },
                "count": {"$sum": 1}
            }},
            {"$project": {
                "timestamp": "$_id.time_bucket",
                "event_type": "$_id.event_type",
                "count": 1,
                "_id": 0
            }},
            {"$sort": {"timestamp": 1}}
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def detect_anomalies(self, threshold_multiplier: float = 2.0) -> list[dict[str, Any]]:
        pipeline = [
            {"$match": {"event_type": "USER_ACTION", "user_id": {"$ne": None}}},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$group": {
                "_id": None,
                "users": {"$push": {"user_id": "$_id", "count": "$count"}},
                "avg_count": {"$avg": "$count"}
            }},
            {"$unwind": "$users"},
            {"$project": {
                "user_id": "$users.user_id",
                "action_count": "$users.count",
                "avg_action_count": "$avg_count",
                "is_anomaly": {"$gte": ["$users.count", {"$multiply": ["$avg_count", threshold_multiplier]}]},
                "_id": 0
            }},
            {"$match": {"is_anomaly": True}},
            {"$project": {"is_anomaly": 0}}
        ]
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
