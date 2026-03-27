from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LogEventType(str, Enum):
    USER_ACTION = "USER_ACTION"
    DB_QUERY = "DB_QUERY"
    ERROR = "ERROR"


class AuditLog(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    event_type: LogEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserActionLog(AuditLog):
    event_type: LogEventType = LogEventType.USER_ACTION
    user_id: str | None = None
    action: str
    details: dict[str, Any] = Field(default_factory=dict)


class DBQueryLog(AuditLog):
    event_type: LogEventType = LogEventType.DB_QUERY
    query: str
    execution_time_ms: float
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorLog(AuditLog):
    event_type: LogEventType = LogEventType.ERROR
    error_type: str
    message: str
    traceback: str | None = None
    path: str | None = None
    user_id: str | None = None
