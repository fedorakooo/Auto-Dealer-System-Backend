from datetime import datetime
from decimal import Decimal

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.dealership_repository import IDealershipRepository
from src.domain.entities.dealership import Dealership
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class DealershipRepository(IDealershipRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, dealership_id: int) -> Dealership | None:
        query = (
            "SELECT d.*, c.name as city_name, c.country FROM dealerships d "
            "LEFT JOIN cities c ON c.id = d.city_id WHERE d.id = $1"
        )
        row = await self._db.fetchrow(query, dealership_id)
        if not row:
            return None
        return self._row_to_dealership(row)

    async def get_all(self, page: int = 1, limit: int = 20) -> tuple[list[Dealership], int]:
        offset = (page - 1) * limit
        query = (
            "SELECT d.*, c.name as city_name, c.country FROM dealerships d "
            "LEFT JOIN cities c ON c.id = d.city_id OFFSET $1 LIMIT $2"
        )
        count_query = "SELECT COUNT(*) FROM dealerships"

        rows = await self._db.fetch(query, offset, limit)
        total = await self._db.fetchval(count_query)

        return [self._row_to_dealership(row) for row in rows], total

    async def get_active(self) -> list[Dealership]:
        query = """
            SELECT d.id, d.name, c.name AS city_name, c.country, d.phone_number, d.email,
                d.address, d.city_id, d.opening_hours, d.latitude, d.longitude, d.is_active,
                d.updated_at
            FROM dealerships d
            LEFT JOIN cities c ON c.id = d.city_id
            WHERE d.is_active = true
            ORDER BY c.country, c.name, d.name
        """
        rows = await self._db.fetch(query)
        return [self._row_to_dealership(row) for row in rows]

    async def get_by_city_id(self, city_id: int) -> list[Dealership]:
        query = """
            SELECT d.*, c.name as city_name, c.country FROM dealerships d
            LEFT JOIN cities c ON c.id = d.city_id
            WHERE d.city_id = $1 AND d.is_active = true
        """
        rows = await self._db.fetch(query, city_id)
        return [self._row_to_dealership(row) for row in rows]

    async def get_by_country(self, country: str) -> list[Dealership]:
        query = """
            SELECT d.*, c.name as city_name, c.country FROM dealerships d
            LEFT JOIN cities c ON c.id = d.city_id
            WHERE c.country = $1 AND d.is_active = true
        """
        rows = await self._db.fetch(query, country)
        return [self._row_to_dealership(row) for row in rows]

    async def create(self, dealership: Dealership) -> Dealership:
        query = """
            INSERT INTO dealerships (
                name, address, city_id, phone_number, email, opening_hours,
                latitude, longitude, is_active
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            dealership.name,
            dealership.address,
            dealership.city_id,
            dealership.phone_number,
            dealership.email,
            dealership.opening_hours,
            float(dealership.latitude) if dealership.latitude else None,
            float(dealership.longitude) if dealership.longitude else None,
            dealership.is_active,
        )
        return self._row_to_dealership(row)

    async def update(self, dealership: Dealership) -> Dealership:
        query = """
            UPDATE dealerships
            SET name = $2, address = $3, city_id = $4, phone_number = $5, email = $6,
                opening_hours = $7, latitude = $8, longitude = $9, is_active = $10,
                updated_at = $11
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            dealership.id,
            dealership.name,
            dealership.address,
            dealership.city_id,
            dealership.phone_number,
            dealership.email,
            dealership.opening_hours,
            float(dealership.latitude) if dealership.latitude else None,
            float(dealership.longitude) if dealership.longitude else None,
            dealership.is_active,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"Dealership with id {dealership.id} not found")
        return self._row_to_dealership(row)

    async def delete(self, dealership_id: int) -> bool:
        query = "DELETE FROM dealerships WHERE id = $1"
        result = await self._db.execute(query, dealership_id)
        return result == "DELETE 1"

    def _row_to_dealership(self, row: asyncpg.Record) -> Dealership:
        return Dealership(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            city_id=row["city_id"],
            phone_number=row.get("phone_number"),
            email=row.get("email"),
            opening_hours=row.get("opening_hours"),
            latitude=Decimal(str(row["latitude"])) if row.get("latitude") else None,
            longitude=Decimal(str(row["longitude"])) if row.get("longitude") else None,
            is_active=row["is_active"],
            updated_at=row.get("updated_at"),
        )
