from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.vehicle_media_repository import IVehicleMediaRepository
from src.domain.entities.vehicle_media import VehicleMedia
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.media_type import MediaType
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class VehicleMediaRepository(IVehicleMediaRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, media_id: UUID) -> VehicleMedia | None:
        query = "SELECT * FROM vehicle_media WHERE id = $1"
        row = await self._db.fetchrow(query, str(media_id))
        if not row:
            return None
        return self._row_to_vehicle_media(row)

    async def get_by_vehicle_id(self, vehicle_id: UUID) -> list[VehicleMedia]:
        query = "SELECT * FROM vehicle_media WHERE vehicle_id = $1 ORDER BY sort_order, updated_at"
        rows = await self._db.fetch(query, str(vehicle_id))
        return [self._row_to_vehicle_media(row) for row in rows]

    async def create(self, vehicle_media: VehicleMedia) -> VehicleMedia:
        query = """
            INSERT INTO vehicle_media (id, vehicle_id, url, media_type, description, sort_order, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(vehicle_media.id),
            str(vehicle_media.vehicle_id),
            vehicle_media.url,
            vehicle_media.media_type.value,
            vehicle_media.description,
            vehicle_media.sort_order,
            datetime.utcnow(),
        )
        return self._row_to_vehicle_media(row)

    async def update(self, vehicle_media: VehicleMedia) -> VehicleMedia:
        query = """
            UPDATE vehicle_media
            SET vehicle_id = $2, url = $3, media_type = $4, description = $5, sort_order = $6, updated_at = $7
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(vehicle_media.id),
            str(vehicle_media.vehicle_id),
            vehicle_media.url,
            vehicle_media.media_type.value,
            vehicle_media.description,
            vehicle_media.sort_order,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"VehicleMedia with id {vehicle_media.id} not found")
        return self._row_to_vehicle_media(row)

    async def delete(self, media_id: UUID) -> bool:
        query = "DELETE FROM vehicle_media WHERE id = $1"
        result = await self._db.execute(query, str(media_id))
        return result == "DELETE 1"

    async def delete_by_vehicle_id(self, vehicle_id: UUID) -> int:
        count_query = "SELECT COUNT(*) FROM vehicle_media WHERE vehicle_id = $1::UUID"
        deleted_count = await self._db.fetchval(count_query, str(vehicle_id))

        if deleted_count and deleted_count > 0:
            await self._db.execute(
                "CALL delete_vehicle_media_by_vehicle($1::UUID)",
                str(vehicle_id),
            )

        return deleted_count or 0

    def _row_to_vehicle_media(self, row: asyncpg.Record) -> VehicleMedia:
        return VehicleMedia(
            id=parse_uuid(row["id"]),
            vehicle_id=parse_uuid(row["vehicle_id"]),
            url=row["url"],
            media_type=MediaType(row["media_type"]),
            description=row.get("description"),
            sort_order=row.get("sort_order", 0),
            updated_at=row.get("updated_at"),
        )
