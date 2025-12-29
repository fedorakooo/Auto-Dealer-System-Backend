from typing import Annotated

from fastapi import Depends, Request

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.healthcheck import IDatabaseHealthCheck
from src.domain.abstractions.database.uow import IUnitOfWork
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.database.healthcheck import DatabaseHealthCheck
from src.infrastructure.database.uow import UnitOfWork
from src.logger import get_logger

logger = get_logger(__name__)


async def get_async_engine() -> IDatabaseConnection:
    db_connection = DatabaseConnection()
    await db_connection.connect()
    return db_connection


def get_database_connection(request: Request) -> IDatabaseConnection:
    db_connection: IDatabaseConnection | None = request.app.state.db_connection
    if db_connection is None:
        logger.error("Database connection is not initialized")
        raise RuntimeError("Database connection is not initialized")
    return db_connection


def get_unit_of_work(
    db_connection: Annotated[IDatabaseConnection, Depends(get_database_connection)],
) -> IUnitOfWork:
    return UnitOfWork(db_connection)


def get_database_health_check(
    db_connection: Annotated[IDatabaseConnection, Depends(get_database_connection)],
) -> IDatabaseHealthCheck:
    return DatabaseHealthCheck(db_connection)
