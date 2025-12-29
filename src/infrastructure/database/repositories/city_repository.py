import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.city_repository import ICityRepository
from src.domain.entities.city import City
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class CityRepository(ICityRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, city_id: int) -> City | None:
        query = "SELECT * FROM cities WHERE id = $1"
        row = await self._db.fetchrow(query, city_id)
        if not row:
            return None
        return self._row_to_city(row)

    async def get_all(self) -> list[City]:
        query = "SELECT * FROM cities ORDER BY country, name"
        rows = await self._db.fetch(query)
        return [self._row_to_city(row) for row in rows]

    async def get_by_name_and_country(self, name: str, country: str) -> City | None:
        query = "SELECT * FROM cities WHERE name = $1 AND country = $2"
        row = await self._db.fetchrow(query, name, country)
        if not row:
            return None
        return self._row_to_city(row)

    async def create(self, city: City) -> City:
        query = "INSERT INTO cities (name, country) VALUES ($1, $2) RETURNING *"
        try:
            row = await self._db.fetchrow(query, city.name, city.country)
            return self._row_to_city(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"City with this name and country already exists: {exc}") from exc

    async def update(self, city: City) -> City:
        query = "UPDATE cities SET name = $2, country = $3 WHERE id = $1 RETURNING *"
        try:
            row = await self._db.fetchrow(query, city.id, city.name, city.country)
            if not row:
                raise DatabaseNotFoundError(f"City with id {city.id} not found")
            return self._row_to_city(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"City with this name and country already exists: {exc}") from exc

    async def delete(self, city_id: int) -> bool:
        query = "DELETE FROM cities WHERE id = $1"
        result = await self._db.execute(query, city_id)
        return result == "DELETE 1"

    def _row_to_city(self, row: asyncpg.Record) -> City:
        return City(
            id=row["id"],
            name=row["name"],
            country=row["country"],
        )
