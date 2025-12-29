from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.feature_repository import IFeatureRepository
from src.domain.entities.feature import Feature
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class FeatureRepository(IFeatureRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, feature_id: int) -> Feature | None:
        query = "SELECT * FROM features WHERE id = $1"
        row = await self._db.fetchrow(query, feature_id)
        if not row:
            return None
        return self._row_to_feature(row)

    async def get_all(self) -> list[Feature]:
        query = "SELECT * FROM features ORDER BY name"
        rows = await self._db.fetch(query)
        return [self._row_to_feature(row) for row in rows]

    async def get_by_model_id(self, model_id: UUID) -> list[Feature]:
        query = """
            SELECT f.* FROM features f
            JOIN model_features mf ON f.id = mf.feature_id
            WHERE mf.model_id = $1
            ORDER BY f.name
        """
        rows = await self._db.fetch(query, str(model_id))
        return [self._row_to_feature(row) for row in rows]

    async def get_by_custom_order_id(self, custom_order_id: UUID) -> list[Feature]:
        query = """
            SELECT f.* FROM features f
            JOIN custom_order_features cof ON f.id = cof.feature_id
            WHERE cof.custom_order_id = $1
            ORDER BY f.name
        """
        rows = await self._db.fetch(query, str(custom_order_id))
        return [self._row_to_feature(row) for row in rows]

    async def create(self, feature: Feature) -> Feature:
        query = "INSERT INTO features (name, description) VALUES ($1, $2) RETURNING *"
        try:
            row = await self._db.fetchrow(query, feature.name, feature.description)
            return self._row_to_feature(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Feature with this name already exists: {exc}") from exc

    async def update(self, feature: Feature) -> Feature:
        query = "UPDATE features SET name = $2, description = $3 WHERE id = $1 RETURNING *"
        try:
            row = await self._db.fetchrow(query, feature.id, feature.name, feature.description)
            if not row:
                raise DatabaseNotFoundError(f"Feature with id {feature.id} not found")
            return self._row_to_feature(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Feature with this name already exists: {exc}") from exc

    async def delete(self, feature_id: int) -> bool:
        query = "DELETE FROM features WHERE id = $1"
        result = await self._db.execute(query, feature_id)
        return result == "DELETE 1"

    async def add_to_model(self, model_id: UUID, feature_id: int) -> bool:
        query = "INSERT INTO model_features (model_id, feature_id) VALUES ($1, $2) ON CONFLICT DO NOTHING"
        result = await self._db.execute(query, str(model_id), feature_id)
        return result == "INSERT 0 1"

    async def remove_from_model(self, model_id: UUID, feature_id: int) -> bool:
        query = "DELETE FROM model_features WHERE model_id = $1 AND feature_id = $2"
        result = await self._db.execute(query, str(model_id), feature_id)
        return result == "DELETE 1"

    async def add_to_custom_order(self, custom_order_id: UUID, feature_id: int) -> bool:
        query = "INSERT INTO custom_order_features (custom_order_id, feature_id) VALUES ($1, $2) ON CONFLICT DO NOTHING"
        result = await self._db.execute(query, str(custom_order_id), feature_id)
        return result == "INSERT 0 1"

    async def remove_from_custom_order(self, custom_order_id: UUID, feature_id: int) -> bool:
        query = "DELETE FROM custom_order_features WHERE custom_order_id = $1 AND feature_id = $2"
        result = await self._db.execute(query, str(custom_order_id), feature_id)
        return result == "DELETE 1"

    def _row_to_feature(self, row: asyncpg.Record) -> Feature:
        return Feature(
            id=row["id"],
            name=row["name"],
            description=row.get("description"),
        )
