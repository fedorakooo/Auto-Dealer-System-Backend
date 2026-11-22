from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.vehicle_repository import IVehicleRepository
from src.domain.entities.vehicle import Vehicle
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.filters import VehicleFilter
from src.domain.value_objects.vehicle_status import VehicleStatus
from src.infrastructure.database.audit_context import set_audit_context
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class VehicleRepository(IVehicleRepository):
    """PostgreSQL repository for vehicles."""

    def __init__(self, db_connection: IDatabaseConnection) -> None:
        self._db = db_connection

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        """Returns one vehicle by ID or None."""
        query = "SELECT * FROM get_vehicle_with_details($1::UUID, NULL)"
        row = await self._db.fetchrow(query, str(vehicle_id))
        if not row:
            return None
        return self._row_to_vehicle(row)

    async def get_by_vin(self, vin: str) -> Vehicle | None:
        """Returns one vehicle by VIN or None."""
        query = "SELECT * FROM get_vehicle_with_details(NULL, $1)"
        row = await self._db.fetchrow(query, vin)
        if not row:
            return None
        return self._row_to_vehicle(row)

    async def get_vehicles(self, vehicle_filter: VehicleFilter) -> tuple[list[Vehicle], int]:
        """Returns vehicles based on filter."""
        f = vehicle_filter
        filter_args = (
            str(f.model_id) if f.model_id else None,
            str(f.trim_id) if f.trim_id else None,
            f.dealership_id,
            f.status.value if f.status else None,
            Decimal(str(f.min_price)) if f.min_price is not None else None,
            Decimal(str(f.max_price)) if f.max_price is not None else None,
            f.model_name,
            f.body_type,
            f.fuel_type.value if f.fuel_type else None,
            f.transmission_type.value if f.transmission_type else None,
        )
        filter_params = """
            $1::UUID, $2::UUID, $3::INTEGER, $4::vehicle_lifecycle_status, $5::DECIMAL, $6::DECIMAL,
            $7::VARCHAR, $8::VARCHAR, $9::fuel_type, $10::transmission_type
        """
        rows = await self._db.fetch(
            f"SELECT * FROM get_vehicles_filtered({filter_params}, "
            "$11::VARCHAR, $12::VARCHAR, $13::INTEGER, $14::INTEGER)",
            *filter_args,
            f.sort_by.value if f.sort_by else "created_at",
            f.order_by.value.upper(),
            (f.page - 1) * f.limit,
            f.limit,
        )
        total = await self._db.fetchval(f"SELECT count_vehicles_filtered({filter_params})", *filter_args)
        return [self._row_to_vehicle(row) for row in rows], total

    async def get_model_ids(self, vehicle_ids: list[UUID]) -> dict[UUID, UUID]:
        """Returns the model of each given vehicle; unknown vehicles are omitted."""
        if not vehicle_ids:
            return {}
        rows = await self._db.fetch(
            "SELECT id, model_id FROM vehicles WHERE id = ANY($1::UUID[])", [str(v) for v in vehicle_ids]
        )
        return {parse_uuid(row["id"]): parse_uuid(row["model_id"]) for row in rows}

    async def get_model_stock_stats(self, model_ids: list[UUID]) -> dict[UUID, tuple[int, Decimal | None]]:
        """Returns (in-stock count, lowest in-stock price) per model; models without stock are omitted."""
        if not model_ids:
            return {}
        rows = await self._db.fetch(
            "SELECT * FROM get_model_stock_stats($1::UUID[])", [str(model_id) for model_id in model_ids]
        )
        return {
            parse_uuid(row["model_id"]): (
                row["vehicles_in_stock"],
                Decimal(str(row["min_price"])) if row["min_price"] is not None else None,
            )
            for row in rows
        }

    async def create(self, vehicle: Vehicle) -> Vehicle:
        """Creates a new vehicle and returns the created vehicle."""
        query = """
            INSERT INTO vehicles (
                model_id, trim_id, dealership_id, vin, production_year, exterior_color,
                interior_color, price, status, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::vehicle_lifecycle_status, $10)
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(vehicle.model_id),
                str(vehicle.trim_id),
                vehicle.dealership_id,
                vehicle.vin,
                vehicle.production_year,
                vehicle.exterior_color,
                vehicle.interior_color,
                float(vehicle.price),
                vehicle.status.value,
                vehicle.created_at or datetime.utcnow(),
            )
            return self._row_to_vehicle(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Vehicle with this VIN already exists: {exc}") from exc

    async def update(self, vehicle: Vehicle) -> Vehicle:
        """Updates a vehicle and returns the updated vehicle."""
        query = """
            UPDATE vehicles
            SET model_id = $2, trim_id = $3, dealership_id = $4, vin = $5, production_year = $6,
                exterior_color = $7, interior_color = $8, price = $9,
                updated_at = $10
            WHERE id = $1
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(vehicle.id),
                str(vehicle.model_id),
                str(vehicle.trim_id),
                vehicle.dealership_id,
                vehicle.vin,
                vehicle.production_year,
                vehicle.exterior_color,
                vehicle.interior_color,
                float(vehicle.price),
                datetime.utcnow(),
            )
            if not row:
                raise DatabaseNotFoundError(f"Vehicle with id {vehicle.id} not found")
            return self._row_to_vehicle(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Vehicle with this VIN already exists: {exc}") from exc

    async def update_status(
        self, vehicle_id: UUID, status: VehicleStatus, changed_by: UUID | None = None, reason: str | None = None
    ) -> bool:
        """Changes the vehicle lifecycle status and records who did it."""
        await set_audit_context(self._db, changed_by, reason)
        result = await self._db.execute(
            "UPDATE vehicles SET status = $2::vehicle_lifecycle_status WHERE id = $1", str(vehicle_id), status.value
        )
        return result == "UPDATE 1"

    async def delete(self, vehicle_id: UUID) -> bool:
        """Deletes a vehicle by its ID."""
        query = "DELETE FROM vehicles WHERE id = $1"
        result = await self._db.execute(query, str(vehicle_id))
        return result == "DELETE 1"

    def _row_to_vehicle(self, row: asyncpg.Record) -> Vehicle:
        return Vehicle(
            id=parse_uuid(row["id"]),
            model_id=parse_uuid(row["model_id"]),
            trim_id=parse_uuid(row["trim_id"]),
            dealership_id=row["dealership_id"],
            vin=row["vin"],
            production_year=row["production_year"],
            exterior_color=row["exterior_color"],
            interior_color=row.get("interior_color"),
            price=Decimal(str(row["price"])),
            status=VehicleStatus(row["status"]),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
