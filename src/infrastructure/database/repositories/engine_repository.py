import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.engine_repository import IEngineRepository
from src.domain.entities.engine import Engine
from src.domain.value_objects.fuel_type import FuelType
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class EngineRepository(IEngineRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, engine_id: int) -> Engine | None:
        query = "SELECT * FROM engines WHERE id = $1"
        row = await self._db.fetchrow(query, engine_id)
        if not row:
            return None
        return self._row_to_engine(row)

    async def get_all(self) -> list[Engine]:
        query = "SELECT * FROM engines ORDER BY name"
        rows = await self._db.fetch(query)
        return [self._row_to_engine(row) for row in rows]

    async def create(self, engine: Engine) -> Engine:
        query = """
            INSERT INTO engines (
                name, engine_code, displacement_cm3, cylinders, horsepower,
                horsepower_electric, torque_nm, fuel_type, configuration, induction, description
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            engine.name,
            engine.engine_code,
            engine.displacement_cm3,
            engine.cylinders,
            engine.horsepower,
            engine.horsepower_electric,
            engine.torque_nm,
            engine.fuel_type.value,
            engine.configuration,
            engine.induction,
            engine.description,
        )
        return self._row_to_engine(row)

    async def update(self, engine: Engine) -> Engine:
        query = """
            UPDATE engines
            SET name = $2, engine_code = $3, displacement_cm3 = $4, cylinders = $5,
                horsepower = $6, horsepower_electric = $7, torque_nm = $8, fuel_type = $9,
                configuration = $10, induction = $11, description = $12
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            engine.id,
            engine.name,
            engine.engine_code,
            engine.displacement_cm3,
            engine.cylinders,
            engine.horsepower,
            engine.horsepower_electric,
            engine.torque_nm,
            engine.fuel_type.value,
            engine.configuration,
            engine.induction,
            engine.description,
        )
        if not row:
            raise DatabaseNotFoundError(f"Engine with id {engine.id} not found")
        return self._row_to_engine(row)

    async def delete(self, engine_id: int) -> bool:
        query = "DELETE FROM engines WHERE id = $1"
        result = await self._db.execute(query, engine_id)
        return result == "DELETE 1"

    def _row_to_engine(self, row: asyncpg.Record) -> Engine:
        return Engine(
            id=row["id"],
            name=row["name"],
            engine_code=row.get("engine_code"),
            displacement_cm3=row.get("displacement_cm3"),
            cylinders=row.get("cylinders"),
            horsepower=row.get("horsepower"),
            horsepower_electric=row.get("horsepower_electric"),
            torque_nm=row.get("torque_nm"),
            fuel_type=FuelType(row["fuel_type"]),
            configuration=row.get("configuration"),
            induction=row.get("induction"),
            description=row.get("description"),
        )
