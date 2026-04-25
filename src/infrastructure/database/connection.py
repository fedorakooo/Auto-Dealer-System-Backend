from typing import Any

import asyncpg
from asyncpg import Connection, Pool

import asyncio
import time

from src.config import settings
from src.infrastructure.mongodb.client import get_mongodb_client_singleton
from src.domain.abstractions.database.connection import IDatabaseConnection
from src.infrastructure.database.exceptions import DatabaseConnectionError
from src.logger import get_logger
from src.application.services.log_service import LogService
from src.infrastructure.mongodb.repositories.log_repository import LogRepository

logger = get_logger(__name__)


def _log_query_async(query: str, execution_time_ms: float, status: str, details: dict | None = None) -> None:
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
    def __init__(self, connection: Connection | None = None):
        self._pool: Pool | None = None
        self._connection: Connection | None = connection

    async def __aenter__(self) -> "IDatabaseConnection":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        await self.disconnect()
        return None

    async def connect(self) -> None:
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
                min_size=1,
                max_size=10,
            )
            logger.info("Database connection pool created successfully")
        except Exception as exc:
            logger.error(f"Failed to create database pool: {exc}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to create database pool: {exc}") from exc

    async def disconnect(self) -> None:
        if self._pool:
            logger.debug("Closing database connection pool")
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")

    async def acquire(self) -> Connection:
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        return await self._pool.acquire()

    async def release(self, connection: Connection) -> None:
        if self._pool:
            await self._pool.release(connection)

    async def execute(self, query: str, *args) -> str:
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
            args_str = [str(a) for a in args]
            _log_query_async(query, exec_time, status, {"args": args_str})

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
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
            args_str = [str(a) for a in args]
            _log_query_async(query, exec_time, status, {"args": args_str})

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
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
            args_str = [str(a) for a in args]
            _log_query_async(query, exec_time, status, {"args": args_str})

    async def fetchval(self, query: str, *args) -> Any:
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
            args_str = [str(a) for a in args]
            _log_query_async(query, exec_time, status, {"args": args_str})

    @property
    def is_connected(self) -> bool:
        return self._pool is not None or self._connection is not None
