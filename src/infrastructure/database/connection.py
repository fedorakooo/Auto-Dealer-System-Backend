from typing import Any

import asyncpg
from asyncpg import Connection, Pool

from src.config import settings
from src.domain.abstractions.database.connection import IDatabaseConnection
from src.infrastructure.database.exceptions import DatabaseConnectionError
from src.logger import get_logger

logger = get_logger(__name__)


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
        if self._connection:
            return await self._connection.execute(query, *args)
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        if self._connection:
            return await self._connection.fetch(query, *args)
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        if self._connection:
            return await self._connection.fetchrow(query, *args)
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        if self._connection:
            return await self._connection.fetchval(query, *args)
        if not self._pool:
            raise DatabaseConnectionError("Database pool is not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @property
    def is_connected(self) -> bool:
        return self._pool is not None or self._connection is not None
