from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.healthcheck import IDatabaseHealthCheck
from src.domain.exceptions.health_check_errors import DatabaseHealthCheckError


class DatabaseHealthCheck(IDatabaseHealthCheck):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def check_health(self) -> bool:
        try:
            result = await self._db.fetchval("SELECT 1")
            return result == 1
        except Exception as exc:
            raise DatabaseHealthCheckError(f"Database health check failed: {exc}") from exc
