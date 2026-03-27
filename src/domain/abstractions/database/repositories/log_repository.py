from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.log import AuditLog


class ILogRepository(ABC):
    @abstractmethod
    async def create(self, log: AuditLog) -> str:
        pass

    @abstractmethod
    async def get_logs(self, filters: dict[str, Any], limit: int = 100, skip: int = 0) -> list[dict[str, Any]]:
        pass
