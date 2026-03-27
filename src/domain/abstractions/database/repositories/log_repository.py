from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.domain.entities.log import AuditLog


class ILogRepository(ABC):
    @abstractmethod
    async def create(self, log: AuditLog) -> str:
        pass

    @abstractmethod
    async def get_logs(self, filters: dict[str, Any], limit: int = 100, skip: int = 0) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_activity_stats(self, period: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_crud_stats(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_time_series(self, start_time: datetime, end_time: datetime, interval: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def detect_anomalies(self, threshold_multiplier: float = 2.0) -> list[dict[str, Any]]:
        pass
