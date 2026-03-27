"""Application lifespan context for startup/shutdown hooks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies.database import get_async_engine
from src.api.dependencies.redis import get_redis
from src.infrastructure.redis.client import RedisClient
from src.infrastructure.mongodb.client import mongodb_client
from src.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting application...")

    redis = None
    async_engine = None

    try:
        redis = get_redis()
        logger.debug("Redis client initialized")

        async_engine = await get_async_engine()
        logger.debug("Database engine initialized")

        await mongodb_client.connect()
        logger.debug("MongoDB client initialized")

        redis_client = RedisClient(redis)
        app.state.redis_client = redis_client
        app.state.redis = redis
        app.state.db_connection = async_engine

        logger.info("Application started successfully")
        yield

    except Exception as exc:
        logger.error(f"Error during application startup: {exc}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down application...")
        if redis:
            await redis.aclose()
            logger.debug("Redis connection closed")
        if async_engine:
            await async_engine.disconnect()
            logger.debug("Database connection closed")
        
        await mongodb_client.close()
        logger.debug("MongoDB connection closed")
        logger.info("Application shutdown complete")
