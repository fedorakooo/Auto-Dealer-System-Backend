from abc import ABC, abstractmethod
from typing import Any

import asyncpg
from asyncpg import Connection


class IDatabaseConnection(ABC):
    """Interface for database connection operations."""

    @abstractmethod
    async def __aenter__(self) -> "IDatabaseConnection":
        """Enters the async context manager."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        """Exits the async context manager."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Establishes a connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Closes the connection to the database."""
        pass

    @abstractmethod
    async def acquire(self) -> Connection:
        """Acquires a connection from the pool."""
        pass

    @abstractmethod
    async def release(self, connection: Connection) -> None:
        """Releases a connection back to the pool."""
        pass

    @abstractmethod
    async def execute(self, query: str, *args) -> str:
        """Executes a query and returns the result."""
        pass

    @abstractmethod
    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        """Fetches multiple rows from the database."""
        pass

    @abstractmethod
    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        """Fetches one row from the database or None."""
        pass

    @abstractmethod
    async def fetchval(self, query: str, *args) -> Any:
        """Fetches a single value from the database."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Returns True if the database is connected, False otherwise."""
        pass
