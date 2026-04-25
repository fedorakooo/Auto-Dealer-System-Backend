import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.abstractions.redis.redis_client import IRedisClient
from src.domain.abstractions.redis.session_repository import ISessionRepository
from src.domain.entities.session import UserSession
from src.logger import get_logger

logger = get_logger(__name__)


class RedisSessionRepository(ISessionRepository):
    """Redis implementation for user sessions."""

    def __init__(self, redis_client: IRedisClient):
        self.redis = redis_client

    def _get_key(self, session_id: UUID) -> str:
        return f"session:{session_id}"

    async def save(self, session: UserSession, default_ttl: int = 3600) -> None:
        key = self._get_key(session.id)
        session_data = {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "is_active": session.is_active,
        }
        try:
            await self.redis.setex(key, default_ttl, json.dumps(session_data))
            logger.debug(f"[SESSION SAVE] Session {session.id} for user {session.user_id}")
        except Exception as exc:
            logger.error(f"Failed to save session {session.id}: {exc}", exc_info=True)

    async def get_by_id(self, session_id: UUID) -> Optional[UserSession]:
        key = self._get_key(session_id)
        try:
            data_str = await self.redis.get(key)
            if not data_str:
                return None
            data = json.loads(data_str)
            return UserSession(
                id=UUID(data["id"]),
                user_id=UUID(data["user_id"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"]),
                is_active=data.get("is_active", True),
            )
        except Exception as exc:
            logger.error(f"Failed to get session {session_id}: {exc}", exc_info=True)
            return None

    async def delete(self, session_id: UUID) -> bool:
        key = self._get_key(session_id)
        try:
            result = await self.redis.delete(key)
            logger.debug(f"[SESSION DELETE] Session {session_id}")
            return bool(result)
        except Exception as exc:
            logger.error(f"Failed to delete session {session_id}: {exc}", exc_info=True)
            return False
