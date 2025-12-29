from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.favorite_repository import IFavoriteRepository
from src.domain.entities.vehicle import Vehicle
from src.domain.utils.uuid_helpers import parse_uuid


class FavoriteRepository(IFavoriteRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_customer_id(self, customer_id: UUID) -> list[Vehicle]:
        query = """
            SELECT v.* FROM vehicles v
            JOIN favorites f ON f.vehicle_id = v.id
            WHERE f.customer_id = $1 AND v.is_active = true
            ORDER BY v.created_at DESC
        """
        rows = await self._db.fetch(query, str(customer_id))
        return [self._row_to_vehicle(row) for row in rows]

    async def add(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        query = "INSERT INTO favorites (customer_id, vehicle_id) VALUES ($1, $2) ON CONFLICT DO NOTHING"
        result = await self._db.execute(query, str(customer_id), str(vehicle_id))
        return result == "INSERT 0 1"

    async def remove(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        query = "DELETE FROM favorites WHERE customer_id = $1 AND vehicle_id = $2"
        result = await self._db.execute(query, str(customer_id), str(vehicle_id))
        return result == "DELETE 1"

    async def exists(self, customer_id: UUID, vehicle_id: UUID) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM favorites WHERE customer_id = $1 AND vehicle_id = $2)"
        result = await self._db.fetchval(query, str(customer_id), str(vehicle_id))
        return result

    def _row_to_vehicle(self, row: asyncpg.Record) -> Vehicle:
        return Vehicle(
            id=parse_uuid(row["id"]),
            model_id=parse_uuid(row["model_id"]),
            dealership_id=row["dealership_id"],
            vin=row["vin"],
            production_year=row["production_year"],
            exterior_color=row["exterior_color"],
            interior_color=row.get("interior_color"),
            price=Decimal(str(row["price"])),
            is_active=row["is_active"],
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
