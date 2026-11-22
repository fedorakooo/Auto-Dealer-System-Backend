from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.model_repository import IModelRepository
from src.domain.entities.model import Model
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.filters import ModelFilter
from src.infrastructure.database.exceptions import DatabaseNotFoundError

MODEL_COLUMNS = """
    id, body_type_id, name, model_code, is_in_production, production_year_start, production_year_end,
    description, number_of_seats, number_of_doors, length_mm, width_mm, height_mm, created_at, updated_at
"""


class ModelRepository(IModelRepository):
    """PostgreSQL repository for vehicle models."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_by_id(self, model_id: UUID) -> Model | None:
        """Returns one model by ID or None."""
        row = await self._db.fetchrow(f"SELECT {MODEL_COLUMNS} FROM models WHERE id = $1", str(model_id))
        if not row:
            return None
        return self._row_to_model(row)

    async def get_models(self, model_filter: ModelFilter) -> tuple[list[Model], int]:
        """Returns models based on filter."""
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
        """Returns active models by body type with pagination."""
        offset = (page - 1) * limit
        query = f"""
            SELECT {MODEL_COLUMNS}
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
        """Returns active models by production year range with pagination."""
        offset = (page - 1) * limit
        query = f"""
            SELECT {MODEL_COLUMNS}
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
        """Creates a new model and returns the created model."""
        query = f"""
            INSERT INTO models (
                id, body_type_id, name, model_code, is_in_production, production_year_start,
                production_year_end, description, number_of_seats, number_of_doors,
                length_mm, width_mm, height_mm
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING {MODEL_COLUMNS}
        """
        row = await self._db.fetchrow(
            query,
            str(model.id),
            model.body_type_id,
            model.name,
            model.model_code,
            model.is_in_production,
            model.production_year_start,
            model.production_year_end,
            model.description,
            model.number_of_seats,
            model.number_of_doors,
            model.length_mm,
            model.width_mm,
            model.height_mm,
        )
        return self._row_to_model(row)

    async def update(self, model: Model) -> Model:
        """Updates a model and returns the updated model."""
        query = f"""
            UPDATE models
            SET body_type_id = $2, name = $3, model_code = $4, is_in_production = $5,
                production_year_start = $6, production_year_end = $7, description = $8,
                number_of_seats = $9, number_of_doors = $10, length_mm = $11, width_mm = $12,
                height_mm = $13, updated_at = $14
            WHERE id = $1
            RETURNING {MODEL_COLUMNS}
        """
        row = await self._db.fetchrow(
            query,
            str(model.id),
            model.body_type_id,
            model.name,
            model.model_code,
            model.is_in_production,
            model.production_year_start,
            model.production_year_end,
            model.description,
            model.number_of_seats,
            model.number_of_doors,
            model.length_mm,
            model.width_mm,
            model.height_mm,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"Model with id {model.id} not found")
        return self._row_to_model(row)

    async def delete(self, model_id: UUID) -> bool:
        """Deletes a model by its ID."""
        query = "DELETE FROM models WHERE id = $1"
        result = await self._db.execute(query, str(model_id))
        return result == "DELETE 1"

    @staticmethod
    def _row_to_model(row: asyncpg.Record) -> Model:
        return Model(
            id=parse_uuid(row["id"]),
            body_type_id=row["body_type_id"],
            name=row["name"],
            model_code=row["model_code"],
            is_in_production=row["is_in_production"],
            production_year_start=row["production_year_start"],
            production_year_end=row["production_year_end"],
            description=row["description"],
            number_of_seats=row["number_of_seats"],
            number_of_doors=row["number_of_doors"],
            length_mm=row["length_mm"],
            width_mm=row["width_mm"],
            height_mm=row["height_mm"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
