from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.trim_repository import ITrimRepository
from src.domain.entities.trim import Trim
from src.domain.exceptions.trim_errors import TrimInUseError
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.drive_type import DriveType
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class TrimRepository(ITrimRepository):
    """PostgreSQL repository for trims."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_by_id(self, trim_id: UUID) -> Trim | None:
        """Returns one trim by ID or None."""
        row = await self._db.fetchrow("SELECT * FROM trims WHERE id = $1", str(trim_id))
        return self._row_to_trim(row) if row else None

    async def get_by_model_id(self, model_id: UUID) -> list[Trim]:
        """Returns all trims of a model."""
        rows = await self._db.fetch("SELECT * FROM trims WHERE model_id = $1 ORDER BY name", str(model_id))
        return [self._row_to_trim(row) for row in rows]

    async def create(self, trim: Trim) -> Trim:
        """Creates a new trim and returns the created trim."""
        query = """
            INSERT INTO trims (
                id, model_id, name, engine_id, transmission_id, drive_type, max_speed_kmh,
                acceleration_0_100_sec, fuel_tank_capacity_l, curb_weight_kg, gross_weight_kg
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(trim.id),
                str(trim.model_id),
                trim.name,
                trim.engine_id,
                trim.transmission_id,
                trim.drive_type.value if trim.drive_type else None,
                trim.max_speed_kmh,
                trim.acceleration_0_100_sec,
                trim.fuel_tank_capacity_l,
                trim.curb_weight_kg,
                trim.gross_weight_kg,
            )
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError("name") from exc
        return self._row_to_trim(row)

    async def update(self, trim: Trim) -> Trim:
        """Updates a trim and returns the updated trim."""
        query = """
            UPDATE trims
            SET name = $2, engine_id = $3, transmission_id = $4, drive_type = $5, max_speed_kmh = $6,
                acceleration_0_100_sec = $7, fuel_tank_capacity_l = $8, curb_weight_kg = $9,
                gross_weight_kg = $10, updated_at = $11
            WHERE id = $1
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(trim.id),
                trim.name,
                trim.engine_id,
                trim.transmission_id,
                trim.drive_type.value if trim.drive_type else None,
                trim.max_speed_kmh,
                trim.acceleration_0_100_sec,
                trim.fuel_tank_capacity_l,
                trim.curb_weight_kg,
                trim.gross_weight_kg,
                datetime.utcnow(),
            )
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError("name") from exc
        if not row:
            raise DatabaseNotFoundError("Trim")
        return self._row_to_trim(row)

    async def delete(self, trim_id: UUID) -> bool:
        """Deletes a trim by its ID."""
        try:
            result = await self._db.execute("DELETE FROM trims WHERE id = $1", str(trim_id))
        except asyncpg.ForeignKeyViolationError as exc:
            raise TrimInUseError(str(trim_id)) from exc
        return result == "DELETE 1"

    @staticmethod
    def _row_to_trim(row: asyncpg.Record) -> Trim:
        return Trim(
            id=parse_uuid(row["id"]),
            model_id=parse_uuid(row["model_id"]),
            name=row["name"],
            engine_id=row["engine_id"],
            transmission_id=row["transmission_id"],
            drive_type=DriveType(row["drive_type"]) if row["drive_type"] else None,
            max_speed_kmh=row["max_speed_kmh"],
            acceleration_0_100_sec=(
                Decimal(str(row["acceleration_0_100_sec"])) if row["acceleration_0_100_sec"] is not None else None
            ),
            fuel_tank_capacity_l=row["fuel_tank_capacity_l"],
            curb_weight_kg=row["curb_weight_kg"],
            gross_weight_kg=row["gross_weight_kg"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
