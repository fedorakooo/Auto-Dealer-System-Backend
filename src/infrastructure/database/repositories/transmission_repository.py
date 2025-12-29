import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.transmission_repository import ITransmissionRepository
from src.domain.entities.transmission import Transmission
from src.domain.value_objects.transmission_type import TransmissionType
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class TransmissionRepository(ITransmissionRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, transmission_id: int) -> Transmission | None:
        query = "SELECT * FROM transmissions WHERE id = $1"
        row = await self._db.fetchrow(query, transmission_id)
        if not row:
            return None
        return self._row_to_transmission(row)

    async def get_all(self) -> list[Transmission]:
        query = "SELECT * FROM transmissions ORDER BY name"
        rows = await self._db.fetch(query)
        return [self._row_to_transmission(row) for row in rows]

    async def create(self, transmission: Transmission) -> Transmission:
        query = (
            "INSERT INTO transmissions (name, type, number_of_gears, description) VALUES ($1, $2, $3, $4) RETURNING *"
        )
        try:
            row = await self._db.fetchrow(
                query,
                transmission.name,
                transmission.type.value,
                transmission.number_of_gears,
                transmission.description,
            )
            return self._row_to_transmission(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Transmission with this name already exists: {exc}") from exc

    async def update(self, transmission: Transmission) -> Transmission:
        query = (
            "UPDATE transmissions SET name = $2, type = $3, number_of_gears = $4, "
            "description = $5 WHERE id = $1 RETURNING *"
        )
        try:
            row = await self._db.fetchrow(
                query,
                transmission.id,
                transmission.name,
                transmission.type.value,
                transmission.number_of_gears,
                transmission.description,
            )
            if not row:
                raise DatabaseNotFoundError(f"Transmission with id {transmission.id} not found")
            return self._row_to_transmission(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Transmission with this name already exists: {exc}") from exc

    async def delete(self, transmission_id: int) -> bool:
        query = "DELETE FROM transmissions WHERE id = $1"
        result = await self._db.execute(query, transmission_id)
        return result == "DELETE 1"

    def _row_to_transmission(self, row: asyncpg.Record) -> Transmission:
        return Transmission(
            id=row["id"],
            name=row["name"],
            type=TransmissionType(row["type"]),
            number_of_gears=row["number_of_gears"],
            description=row.get("description"),
        )
