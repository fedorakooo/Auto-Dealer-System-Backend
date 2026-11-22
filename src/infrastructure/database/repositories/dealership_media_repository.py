from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.dealership_media_repository import IDealershipMediaRepository
from src.domain.entities.dealership_media import DealershipMedia
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.media_type import MediaType
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class DealershipMediaRepository(IDealershipMediaRepository):
    """PostgreSQL repository for dealership photos."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_by_id(self, media_id: UUID) -> DealershipMedia | None:
        """Returns one dealership media by ID or None."""
        row = await self._db.fetchrow("SELECT * FROM dealership_media WHERE id = $1", str(media_id))
        return self._row_to_media(row) if row else None

    async def get_by_dealership_id(self, dealership_id: int) -> list[DealershipMedia]:
        """Returns the gallery of a dealership ordered by sort_order."""
        query = "SELECT * FROM dealership_media WHERE dealership_id = $1 ORDER BY sort_order, updated_at, id"
        rows = await self._db.fetch(query, dealership_id)
        return [self._row_to_media(row) for row in rows]

    async def get_cover_ids(self, dealership_ids: list[int]) -> dict[int, UUID]:
        """Returns the first image of each dealership gallery, keyed by dealership ID."""
        if not dealership_ids:
            return {}
        rows = await self._db.fetch("SELECT * FROM get_dealership_cover_media($1::INTEGER[])", dealership_ids)
        return {row["dealership_id"]: parse_uuid(row["media_id"]) for row in rows}

    async def create(self, media: DealershipMedia) -> DealershipMedia:
        """Creates a dealership media record."""
        query = """
            INSERT INTO dealership_media (id, dealership_id, url, media_type, description, sort_order, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, now())
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(media.id),
            media.dealership_id,
            media.url,
            media.media_type.value,
            media.description,
            media.sort_order,
        )
        return self._row_to_media(row)

    async def update(self, media: DealershipMedia) -> DealershipMedia:
        """Updates a dealership media record."""
        query = """
            UPDATE dealership_media
            SET description = $2, sort_order = $3
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(query, str(media.id), media.description, media.sort_order)
        if not row:
            raise DatabaseNotFoundError(f"DealershipMedia with id {media.id} not found")
        return self._row_to_media(row)

    async def delete(self, media_id: UUID) -> bool:
        """Deletes a dealership media record by its ID."""
        result = await self._db.execute("DELETE FROM dealership_media WHERE id = $1", str(media_id))
        return result == "DELETE 1"

    def _row_to_media(self, row: asyncpg.Record) -> DealershipMedia:
        return DealershipMedia(
            id=parse_uuid(row["id"]),
            dealership_id=row["dealership_id"],
            url=row["url"],
            media_type=MediaType(row["media_type"]),
            description=row.get("description"),
            sort_order=row.get("sort_order", 0),
            updated_at=row.get("updated_at"),
        )
