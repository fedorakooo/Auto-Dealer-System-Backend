import asyncio
from contextlib import suppress
from typing import Any

from src.config import settings
from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.logger import get_logger

logger = get_logger(__name__)


class OutboxWorker:
    def __init__(self, database: IDatabaseConnection, pubsub: IPubSubManager):
        self._database = database
        self._pubsub = pubsub
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run(), name="outbox-worker")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _run(self) -> None:
        while True:
            try:
                processed = await self._process_one()
                if not processed:
                    await asyncio.sleep(settings.pubsub_settings.OUTBOX_POLL_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Unexpected outbox worker iteration failure")
                await asyncio.sleep(settings.pubsub_settings.OUTBOX_POLL_INTERVAL_SECONDS)

    async def _process_one(self) -> bool:
        connection = await self._database.acquire()
        event: dict[str, Any] | None = None
        try:
            transaction = connection.transaction()
            await transaction.start()
            try:
                row = await connection.fetchrow(
                    """
                    SELECT id, aggregate_type, aggregate_id, event_type, payload, attempts
                    FROM outbox_events
                    WHERE status IN ('pending', 'processing') AND available_at <= now()
                      AND attempts < $1
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED LIMIT 1
                    """,
                    settings.pubsub_settings.OUTBOX_MAX_ATTEMPTS,
                )
                if row:
                    event = dict(row)
                    await connection.execute(
                        """
                        UPDATE outbox_events
                        SET status = 'processing', attempts = attempts + 1,
                            available_at = now() + interval '30 seconds'
                        WHERE id = $1
                        """,
                        row["id"],
                    )
            except Exception:
                await transaction.rollback()
                raise
            else:
                await transaction.commit()
            if event is None:
                return False
            await self._pubsub.publish(
                settings.pubsub_settings.outbox_channel,
                {
                    "id": str(event["id"]),
                    "aggregate_type": event["aggregate_type"],
                    "aggregate_id": event["aggregate_id"],
                    "event_type": event["event_type"],
                    "payload": event["payload"],
                },
            )
            await connection.execute(
                """
                UPDATE outbox_events SET status = 'published', published_at = now(), last_error = NULL
                WHERE id = $1
                """,
                event["id"],
            )
            await connection.execute(
                """
                DELETE FROM outbox_events
                WHERE status = 'published' AND published_at < now() - ($1 * interval '1 day')
                """,
                settings.pubsub_settings.OUTBOX_RETENTION_DAYS,
            )
            return True
        except Exception as exc:
            if event is not None:
                attempts = int(event["attempts"]) + 1
                terminal = attempts >= settings.pubsub_settings.OUTBOX_MAX_ATTEMPTS
                await connection.execute(
                    """
                    UPDATE outbox_events
                    SET status = $2::outbox_event_status, last_error = $3,
                        available_at = now() + (LEAST(300, power(2, $4)) * interval '1 second')
                    WHERE id = $1
                    """,
                    event["id"],
                    "failed" if terminal else "pending",
                    type(exc).__name__,
                    attempts,
                )
            logger.warning("Outbox publish failed: %s", type(exc).__name__)
            return True
        finally:
            await self._database.release(connection)
