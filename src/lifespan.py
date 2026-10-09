"""Application lifespan context for startup/shutdown hooks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies.database import get_async_engine
from src.api.dependencies.mongodb import get_mongodb_client
from src.api.dependencies.redis import get_redis
from src.application.handlers.data_change_handler import DataChangeCacheHandler
from src.application.utils.cache_manager import CacheManager
from src.config import settings
from src.infrastructure.database.migrations import migrate
from src.infrastructure.outbox_worker import OutboxWorker
from src.infrastructure.pubsub.redis_pubsub import RedisPubSubManager
from src.infrastructure.redis.client import RedisClient
from src.infrastructure.startup.employee_seed import seed_employees_if_missing
from src.infrastructure.startup.s3_bootstrap import ensure_s3_bucket
from src.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting application...")

    redis = None
    async_engine = None
    pubsub_manager = None
    mongodb_client = get_mongodb_client()
    outbox_worker = None

    try:
        redis = get_redis()
        logger.debug("Redis client initialized")

        async_engine = await get_async_engine()
        logger.debug("Database engine initialized")

        if settings.postgres_settings.POSTGRES_MIGRATE_ON_START:
            migration_connection = await async_engine.acquire()
            try:
                applied_versions = await migrate(migration_connection)
                if applied_versions:
                    logger.info("Applied database migrations: %s", applied_versions)
            finally:
                await async_engine.release(migration_connection)

        await seed_employees_if_missing(async_engine, settings.employee_seed_settings.path)

        await ensure_s3_bucket(settings.s3_settings)

        await mongodb_client.connect()
        logger.debug("MongoDB client initialized")

        redis_client = RedisClient(redis)
        cache = CacheManager(redis_client)
        data_change_handler = DataChangeCacheHandler(cache)

        pubsub_manager = RedisPubSubManager()
        await pubsub_manager.connect()
        await pubsub_manager.subscribe(settings.pubsub_settings.data_changes_channel, data_change_handler.handle)
        logger.debug("Pub/Sub manager initialized and subscribed")

        if settings.pubsub_settings.OUTBOX_ENABLED:
            outbox_worker = OutboxWorker(async_engine, pubsub_manager)
            outbox_worker.start()

        app.state.redis_client = redis_client
        app.state.redis = redis
        app.state.db_connection = async_engine
        app.state.pubsub_manager = pubsub_manager
        app.state.mongodb_client = mongodb_client

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

        if pubsub_manager:
            if outbox_worker:
                await outbox_worker.stop()
            await pubsub_manager.disconnect()
            logger.debug("Pub/Sub manager disconnected")

        await mongodb_client.close()
        logger.debug("MongoDB connection closed")
        logger.info("Application shutdown complete")
