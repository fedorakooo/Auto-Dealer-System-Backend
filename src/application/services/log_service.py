from datetime import datetime
from typing import Any

from src.domain.abstractions.database.repositories.log_repository import ILogRepository
from src.domain.entities.log import DBQueryLog, ErrorLog, UserActionLog


class LogService:
    def __init__(self, log_repository: ILogRepository) -> None:
        self._log_repository = log_repository

    async def log_user_action(
        self, action: str, user_id: str | None = None, details: dict[str, Any] | None = None
    ) -> str:
        log = UserActionLog(action=action, user_id=user_id, details=details or {})
        return await self._log_repository.create(log)

    async def log_db_query(
        self, query: str, execution_time_ms: float, status: str, details: dict[str, Any] | None = None
    ) -> str:
        log = DBQueryLog(query=query, execution_time_ms=execution_time_ms, status=status, details=details or {})
        return await self._log_repository.create(log)

    async def log_error(
        self,
        error_type: str,
        message: str,
        traceback: str | None = None,
        path: str | None = None,
        user_id: str | None = None,
    ) -> str:
        log = ErrorLog(error_type=error_type, message=message, traceback=traceback, path=path, user_id=user_id)
        return await self._log_repository.create(log)

    async def search_logs(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        user_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {}
        if start_time or end_time:
            timestamp_filter = {}
            if start_time:
                timestamp_filter["$gte"] = start_time
            if end_time:
                timestamp_filter["$lte"] = end_time
            filters["timestamp"] = timestamp_filter

        if user_id:
            filters["user_id"] = user_id

        if event_type:
            filters["event_type"] = event_type

        return await self._log_repository.get_logs(filters, limit, skip)

    async def get_activity_stats(self, period: str) -> list[dict[str, Any]]:
        return await self._log_repository.get_activity_stats(period)

    async def get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        return await self._log_repository.get_top_users(limit)

    async def get_crud_stats(self) -> list[dict[str, Any]]:
        return await self._log_repository.get_crud_stats()

    async def get_time_series(self, start_time: datetime, end_time: datetime, interval: str) -> list[dict[str, Any]]:
        return await self._log_repository.get_time_series(start_time, end_time, interval)

    async def detect_anomalies(self, threshold_multiplier: float = 2.0) -> list[dict[str, Any]]:
        return await self._log_repository.detect_anomalies(threshold_multiplier)
