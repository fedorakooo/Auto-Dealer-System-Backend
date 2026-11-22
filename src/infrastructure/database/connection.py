import asyncio
import time
from types import TracebackType
from typing import Any

import asyncpg
from asyncpg import Connection, Pool

from src.application.services.log_service import LogService
from src.config import settings
from src.domain.abstractions.database.connection import IDatabaseConnection
from src.infrastructure.database.exceptions import DatabaseConnectionError
from src.infrastructure.mongodb.client import get_mongodb_client_singleton
from src.infrastructure.mongodb.repositories.log_repository import LogRepository
from src.logger import get_logger

logger = get_logger(__name__)


def _log_query_async(query: str, execution_time_ms: float, status: str, details: dict[str, Any] | None = None) -> None:
    """Schedules persisting query timing to MongoDB without blocking the query."""
    mongodb_client = get_mongodb_client_singleton()
    if mongodb_client.db is not None:
        log_service = LogService(LogRepository(mongodb_client.db.logs))
        asyncio.create_task(
            log_service.log_db_query(
                query=query,
                execution_time_ms=execution_time_ms,
                status=status,
                details=details,
            )
        )


class DatabaseConnection(IDatabaseConnection):
    """asyncpg-backed database connection or pool."""

    def __init__(self, connection: Connection | None = None) -> None:
        self._pool: Pool | None = None
        self._connection: Connection | None = connection

    async def __aenter__(self) -> "IDatabaseConnection":
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        await self.disconnect()
        return None

    async def connect(self) -> None:
        """Establishes a connection to the database."""
        host = settings.postgres_settings.POSTGRES_HOST
        port = settings.postgres_settings.POSTGRES_PORT
        db_name = settings.postgres_settings.POSTGRES_NAME
        logger.debug(f"Connecting to database: {host}:{port}/{db_name}")
        try:
            self._pool = await asyncpg.create_pool(
                host=settings.postgres_settings.POSTGRES_HOST,
                port=int(settings.postgres_settings.POSTGRES_PORT),
                user=settings.postgres_settings.POSTGRES_USER,
                password=settings.postgres_settings.POSTGRES_PASSWORD,
                database=settings.postgres_settings.POSTGRES_NAME,
                min_size=settings.postgres_settings.POSTGRES_POOL_MIN_SIZE,
                max_size=settings.postgres_settings.POSTGRES_POOL_MAX_SIZE,
                command_timeout=settings.postgres_settings.POSTGRES_COMMAND_TIMEOUT,
                max_queries=settings.postgres_settings.POSTGRES_MAX_QUERIES,
                max_inactive_connection_lifetime=settings.postgres_settings.POSTGRES_MAX_INACTIVE_CONNECTION_LIFETIME,
            )
            logger.info("Database connection pool created successfully")
        except Exception as exc:
            logger.error(f"Failed to create database pool: {exc}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to create database pool: {exc}") from exc

    async def disconnect(self) -> None:
        """Closes the connection to the database."""
        if self._pool:
            logger.debug("Closing database connection pool")
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")

    async def acquire(self) -> Connection:
        """Acquires a connection from the pool."""
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        return await self._pool.acquire(timeout=settings.postgres_settings.POSTGRES_ACQUIRE_TIMEOUT)

    async def release(self, connection: Connection) -> None:
        """Releases a connection back to the pool."""
        if self._pool:
            await self._pool.release(connection)

    async def execute(self, query: str, *args: Any) -> str:
        """Executes a query and returns the result."""
        start_time = time.perf_counter()
        status = "SUCCESS"
        try:
            if self._connection:
                return await self._connection.execute(query, *args)
            if not self._pool:
                raise DatabaseConnectionError("Database pool is not initialized")
            async with self._pool.acquire() as conn:
                return await conn.execute(query, *args)
        except Exception as e:
            status = f"ERROR: {type(e).__name__}"
            raise
        finally:
            exec_time = (time.perf_counter() - start_time) * 1000
            _log_query_async(query, exec_time, status, {"parameter_count": len(args)})

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """Fetches multiple rows from the database."""
        start_time = time.perf_counter()
        status = "SUCCESS"
        try:
            if self._connection:
                return await self._connection.fetch(query, *args)
            if not self._pool:
                raise DatabaseConnectionError("Database pool is not initialized")
            async with self._pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            status = f"ERROR: {type(e).__name__}"
            raise
        finally:
            exec_time = (time.perf_counter() - start_time) * 1000
            _log_query_async(query, exec_time, status, {"parameter_count": len(args)})

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """Fetches one row from the database or None."""
        start_time = time.perf_counter()
        status = "SUCCESS"
        try:
            if self._connection:
                return await self._connection.fetchrow(query, *args)
            if not self._pool:
                raise DatabaseConnectionError("Database pool is not initialized")
            async with self._pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except Exception as e:
            status = f"ERROR: {type(e).__name__}"
            raise
        finally:
            exec_time = (time.perf_counter() - start_time) * 1000
            _log_query_async(query, exec_time, status, {"parameter_count": len(args)})

    async def fetchval(self, query: str, *args: Any) -> Any:  # scalar of any column type
        """Fetches a single value from the database."""
        start_time = time.perf_counter()
        status = "SUCCESS"
        try:
            if self._connection:
                return await self._connection.fetchval(query, *args)
            if not self._pool:
                raise DatabaseConnectionError("Database pool is not initialized")
            async with self._pool.acquire() as conn:
                return await conn.fetchval(query, *args)
        except Exception as e:
            status = f"ERROR: {type(e).__name__}"
            raise
        finally:
            exec_time = (time.perf_counter() - start_time) * 1000
            _log_query_async(query, exec_time, status, {"parameter_count": len(args)})

    @property
    def is_connected(self) -> bool:
        """Returns True if the database is connected, False otherwise."""
        return self._pool is not None or self._connection is not None
