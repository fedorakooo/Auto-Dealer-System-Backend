from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.model_repository import IModelRepository
from src.domain.entities.model import Model
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.drive_type import DriveType
from src.domain.value_objects.filters import ModelFilter
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class ModelRepository(IModelRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, model_id: UUID) -> Model | None:
        query = """
            SELECT id, body_type_id, engine_id, transmission_id, name, model_code,
                is_in_production, production_year_start, production_year_end, description,
                drive_type, max_speed_kmh, acceleration_0_100_sec, fuel_tank_capacity_l,
                number_of_seats, number_of_doors, length_mm, width_mm, height_mm,
                curb_weight_kg, gross_weight_kg, created_at, updated_at
            FROM models
            WHERE id = $1
        """
        row = await self._db.fetchrow(query, str(model_id))
        if not row:
            return None
        return self._row_to_model(row)

    async def get_models(self, model_filter: ModelFilter) -> tuple[list[Model], int]:
        offset = (model_filter.page - 1) * model_filter.limit

        sort_by = model_filter.sort_by.value if model_filter.sort_by else "created_at"
        order_direction = model_filter.order_by.value.upper()

        query = """
            SELECT * FROM get_models_filtered(
                $1::VARCHAR,
                $2::BOOLEAN,
                $3::INTEGER,
                $4::INTEGER,
                $5::VARCHAR,
                $6::VARCHAR,
                $7::INTEGER,
                $8::INTEGER
            )
        """
        rows = await self._db.fetch(
            query,
            model_filter.name,
            model_filter.is_in_production,
            model_filter.body_type_id,
            model_filter.engine_id,
            sort_by,
            order_direction,
            offset,
            model_filter.limit,
        )

        count_query = "SELECT count_models_filtered($1, $2, $3, $4)"

        total = await self._db.fetchval(
            count_query,
            model_filter.name,
            model_filter.is_in_production,
            model_filter.body_type_id,
            model_filter.engine_id,
        )

        return [self._row_to_model(row) for row in rows], total

    async def get_active_by_body_type(
        self, body_type_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Model], int]:
        offset = (page - 1) * limit
        query = """
            SELECT id, body_type_id, engine_id, transmission_id, name, model_code,
                is_in_production, production_year_start, production_year_end, description,
                drive_type, number_of_seats, number_of_doors, created_at, updated_at
            FROM models
            WHERE body_type_id = $1 AND is_in_production = true
            ORDER BY production_year_start DESC
            OFFSET $2 LIMIT $3
        """
        count_query = "SELECT COUNT(*) FROM models WHERE body_type_id = $1 AND is_in_production = true"

        rows = await self._db.fetch(query, body_type_id, offset, limit)
        total = await self._db.fetchval(count_query, body_type_id)

        return [self._row_to_model(row) for row in rows], total

    async def get_active_by_production_year_range(
        self, year_start: int, year_end: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Model], int]:
        offset = (page - 1) * limit
        query = """
            SELECT id, body_type_id, engine_id, transmission_id, name, model_code,
                is_in_production, production_year_start, production_year_end, drive_type,
                max_speed_kmh, number_of_seats, number_of_doors
            FROM models
            WHERE production_year_start BETWEEN $1 AND $2 AND is_in_production = true
            ORDER BY production_year_start DESC
            OFFSET $3 LIMIT $4
        """
        count_query = (
            "SELECT COUNT(*) FROM models WHERE production_year_start BETWEEN $1 AND $2 AND is_in_production = true"
        )

        rows = await self._db.fetch(query, year_start, year_end, offset, limit)
        total = await self._db.fetchval(count_query, year_start, year_end)

        return [self._row_to_model(row) for row in rows], total

    async def create(self, model: Model) -> Model:
        query = """
            INSERT INTO models (
                id, body_type_id, engine_id, transmission_id, name, model_code,
                is_in_production, production_year_start, production_year_end, description,
                drive_type, max_speed_kmh, acceleration_0_100_sec, fuel_tank_capacity_l,
                number_of_seats, number_of_doors, length_mm, width_mm, height_mm,
                curb_weight_kg, gross_weight_kg
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(model.id),
            model.body_type_id,
            model.engine_id,
            model.transmission_id,
            model.name,
            model.model_code,
            model.is_in_production,
            model.production_year_start,
            model.production_year_end,
            model.description,
            model.drive_type.value if model.drive_type else None,
            model.max_speed_kmh,
            float(model.acceleration_0_100_sec) if model.acceleration_0_100_sec else None,
            model.fuel_tank_capacity_l,
            model.number_of_seats,
            model.number_of_doors,
            model.length_mm,
            model.width_mm,
            model.height_mm,
            model.curb_weight_kg,
            model.gross_weight_kg,
        )
        return self._row_to_model(row)

    async def update(self, model: Model) -> Model:
        query = """
            UPDATE models
            SET body_type_id = $2, engine_id = $3, transmission_id = $4, name = $5,
                model_code = $6, is_in_production = $7, production_year_start = $8,
                production_year_end = $9, description = $10, drive_type = $11,
                max_speed_kmh = $12, acceleration_0_100_sec = $13, fuel_tank_capacity_l = $14,
                number_of_seats = $15, number_of_doors = $16, length_mm = $17, width_mm = $18,
                height_mm = $19, curb_weight_kg = $20, gross_weight_kg = $21, updated_at = $22
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(model.id),
            model.body_type_id,
            model.engine_id,
            model.transmission_id,
            model.name,
            model.model_code,
            model.is_in_production,
            model.production_year_start,
            model.production_year_end,
            model.description,
            model.drive_type.value if model.drive_type else None,
            model.max_speed_kmh,
            float(model.acceleration_0_100_sec) if model.acceleration_0_100_sec else None,
            model.fuel_tank_capacity_l,
            model.number_of_seats,
            model.number_of_doors,
            model.length_mm,
            model.width_mm,
            model.height_mm,
            model.curb_weight_kg,
            model.gross_weight_kg,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"Model with id {model.id} not found")
        return self._row_to_model(row)

    async def delete(self, model_id: UUID) -> bool:
        query = "DELETE FROM models WHERE id = $1"
        result = await self._db.execute(query, str(model_id))
        return result == "DELETE 1"

    def _row_to_model(self, row: asyncpg.Record) -> Model:
        return Model(
            id=parse_uuid(row["id"]),
            body_type_id=row["body_type_id"],
            engine_id=row["engine_id"],
            transmission_id=row["transmission_id"],
            name=row["name"],
            model_code=row.get("model_code"),
            is_in_production=row.get("is_in_production"),
            production_year_start=row["production_year_start"],
            production_year_end=row.get("production_year_end"),
            description=row.get("description"),
            drive_type=DriveType(row["drive_type"]) if row.get("drive_type") else None,
            max_speed_kmh=row.get("max_speed_kmh"),
            acceleration_0_100_sec=(
                Decimal(str(row["acceleration_0_100_sec"])) if row.get("acceleration_0_100_sec") else None
            ),
            fuel_tank_capacity_l=row.get("fuel_tank_capacity_l"),
            number_of_seats=row.get("number_of_seats"),
            number_of_doors=row.get("number_of_doors"),
            length_mm=row.get("length_mm"),
            width_mm=row.get("width_mm"),
            height_mm=row.get("height_mm"),
            curb_weight_kg=row.get("curb_weight_kg"),
            gross_weight_kg=row.get("gross_weight_kg"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
