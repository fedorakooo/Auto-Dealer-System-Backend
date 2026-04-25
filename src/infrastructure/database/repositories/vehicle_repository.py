from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.vehicle_repository import IVehicleRepository
from src.domain.entities.vehicle import Vehicle
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.filters import VehicleFilter
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class VehicleRepository(IVehicleRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        query = "SELECT * FROM get_vehicle_with_details($1::UUID, NULL)"
        row = await self._db.fetchrow(query, str(vehicle_id))
        if not row:
            return None
        return self._row_to_vehicle(row)

    async def get_by_vin(self, vin: str) -> Vehicle | None:
        query = "SELECT * FROM get_vehicle_with_details(NULL, $1)"
        row = await self._db.fetchrow(query, vin)
        if not row:
            return None
        return self._row_to_vehicle(row)

    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[Vehicle], int]:
        offset = (vehicle_filter.page - 1) * vehicle_filter.limit

        model_id_uuid = UUID(vehicle_filter.model_id) if vehicle_filter.model_id else None
        sort_by = vehicle_filter.sort_by.value if vehicle_filter.sort_by else "created_at"
        order_direction = vehicle_filter.order_by.value.upper()
        min_price = Decimal(str(vehicle_filter.min_price)) if vehicle_filter.min_price is not None else None
        max_price = Decimal(str(vehicle_filter.max_price)) if vehicle_filter.max_price is not None else None

        query = """
            SELECT * FROM get_vehicles_filtered(
                $1::UUID,
                $2::INTEGER,
                $3::BOOLEAN,
                $4::DECIMAL,
                $5::DECIMAL,
                $6::VARCHAR,
                $7::VARCHAR,
                $8::INTEGER,
                $9::INTEGER
            )
        """
        rows = await self._db.fetch(
            query,
            str(model_id_uuid) if model_id_uuid else None,
            vehicle_filter.dealership_id,
            vehicle_filter.is_active,
            float(min_price) if min_price is not None else None,
            float(max_price) if max_price is not None else None,
            sort_by,
            order_direction,
            offset,
            vehicle_filter.limit,
        )

        count_query = """
            SELECT count_vehicles_filtered(
                $1::UUID,
                $2::INTEGER,
                $3::BOOLEAN,
                $4::DECIMAL,
                $5::DECIMAL
            )
        """
        total = await self._db.fetchval(
            count_query,
            str(model_id_uuid) if model_id_uuid else None,
            vehicle_filter.dealership_id,
            vehicle_filter.is_active,
            float(min_price) if min_price is not None else None,
            float(max_price) if max_price is not None else None,
        )

        return [self._row_to_vehicle(row) for row in rows], total

    async def get_by_dealership_id(self, dealership_id: int) -> list[Vehicle]:
        query = """
            SELECT v.*, m.name as model_name, b.name as body_type, e.name as engine_name, t.name as transmission_name
            FROM vehicles v
            LEFT JOIN models m ON m.id = v.model_id
            LEFT JOIN body_types b ON b.id = m.body_type_id
            LEFT JOIN engines e ON e.id = m.engine_id
            LEFT JOIN transmissions t ON t.id = m.transmission_id
            WHERE v.dealership_id = $1 AND v.is_active = true
        """
        rows = await self._db.fetch(query, dealership_id)
        return [self._row_to_vehicle(row) for row in rows]

    async def search_vehicles(
        self,
        model_name: str | None = None,
        body_type: str | None = None,
        fuel_type: str | None = None,
        transmission_type: str | None = None,
        min_price: float = 0,
        max_price: float = 99999999,
        dealership_id: int | None = None,
    ) -> list[Vehicle]:
        query = """
            SELECT v.*, s.model_name
            FROM search_vehicles($1, $2, $3::fuel_type, $4::transmission_type, $5, $6, $7) AS s
            JOIN vehicles v ON v.id = s.vehicle_id
            ORDER BY s.price
        """
        rows = await self._db.fetch(
            query,
            model_name,
            body_type,
            fuel_type,
            transmission_type,
            Decimal(str(min_price)),
            Decimal(str(max_price)),
            dealership_id,
        )
        return [self._row_to_vehicle(row) for row in rows]

    async def create(self, vehicle: Vehicle) -> Vehicle:
        query = """
            INSERT INTO vehicles (
                model_id, dealership_id, vin, production_year, exterior_color,
                interior_color, price, is_active, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(vehicle.model_id),
                vehicle.dealership_id,
                vehicle.vin,
                vehicle.production_year,
                vehicle.exterior_color,
                vehicle.interior_color,
                float(vehicle.price),
                vehicle.is_active,
                vehicle.created_at or datetime.utcnow(),
            )
            return self._row_to_vehicle(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Vehicle with this VIN already exists: {exc}") from exc

    async def update(self, vehicle: Vehicle) -> Vehicle:
        query = """
            UPDATE vehicles
            SET model_id = $2, dealership_id = $3, vin = $4, production_year = $5,
                exterior_color = $6, interior_color = $7, price = $8, is_active = $9,
                updated_at = $10
            WHERE id = $1
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(vehicle.id),
                str(vehicle.model_id),
                vehicle.dealership_id,
                vehicle.vin,
                vehicle.production_year,
                vehicle.exterior_color,
                vehicle.interior_color,
                float(vehicle.price),
                vehicle.is_active,
                datetime.utcnow(),
            )
            if not row:
                raise DatabaseNotFoundError(f"Vehicle with id {vehicle.id} not found")
            return self._row_to_vehicle(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Vehicle with this VIN already exists: {exc}") from exc

    async def delete(self, vehicle_id: UUID) -> bool:
        query = "DELETE FROM vehicles WHERE id = $1"
        result = await self._db.execute(query, str(vehicle_id))
        return result == "DELETE 1"

    def _row_to_vehicle(self, row: asyncpg.Record) -> Vehicle:
        vehicle = Vehicle(
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
        # Note: model_name is not part of Vehicle entity, it's only used in queries
        # If needed, it should be handled at DTO/service level
        return vehicle
