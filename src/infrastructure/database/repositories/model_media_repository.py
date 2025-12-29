from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.model_media_repository import IModelMediaRepository
from src.domain.entities.model_media import ModelMedia
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.media_type import MediaType
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class ModelMediaRepository(IModelMediaRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, media_id: UUID) -> ModelMedia | None:
        query = "SELECT * FROM model_media WHERE id = $1"
        row = await self._db.fetchrow(query, str(media_id))
        if not row:
            return None
        return self._row_to_model_media(row)

    async def get_by_model_id(self, model_id: UUID) -> list[ModelMedia]:
        query = "SELECT * FROM model_media WHERE model_id = $1 ORDER BY sort_order, updated_at"
        rows = await self._db.fetch(query, str(model_id))
        return [self._row_to_model_media(row) for row in rows]

    async def create(self, model_media: ModelMedia) -> ModelMedia:
        query = (
            "INSERT INTO model_media (id, model_id, url, media_type, description, sort_order, updated_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *"
        )
        row = await self._db.fetchrow(
            query,
            str(model_media.id),
            str(model_media.model_id),
            model_media.url,
            model_media.media_type.value,
            model_media.description,
            model_media.sort_order,
            datetime.utcnow(),
        )
        return self._row_to_model_media(row)

    async def update(self, model_media: ModelMedia) -> ModelMedia:
        query = """
            UPDATE model_media
            SET model_id = $2, url = $3, media_type = $4, description = $5, sort_order = $6, updated_at = $7
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(model_media.id),
            str(model_media.model_id),
            model_media.url,
            model_media.media_type.value,
            model_media.description,
            model_media.sort_order,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"ModelMedia with id {model_media.id} not found")
        return self._row_to_model_media(row)

    async def delete(self, media_id: UUID) -> bool:
        query = "DELETE FROM model_media WHERE id = $1"
        result = await self._db.execute(query, str(media_id))
        return result == "DELETE 1"

    async def delete_by_model_id(self, model_id: UUID) -> int:
        count_query = "SELECT COUNT(*) FROM model_media WHERE model_id = $1::UUID"
        deleted_count = await self._db.fetchval(count_query, str(model_id))

        if deleted_count and deleted_count > 0:
            await self._db.execute(
                "CALL delete_model_media_by_model($1::UUID)",
                str(model_id),
            )

        return deleted_count or 0

    def _row_to_model_media(self, row: asyncpg.Record) -> ModelMedia:
        return ModelMedia(
            id=parse_uuid(row["id"]),
            model_id=parse_uuid(row["model_id"]),
            url=row["url"],
            media_type=MediaType(row["media_type"]),
            description=row.get("description"),
            sort_order=row.get("sort_order", 0),
            updated_at=row.get("updated_at"),
        )
