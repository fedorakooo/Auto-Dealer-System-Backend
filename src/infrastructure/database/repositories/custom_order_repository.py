from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.custom_order_repository import ICustomOrderRepository
from src.domain.entities.custom_order import CustomOrder
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.custom_order_status import CustomOrderStatus
from src.infrastructure.database.exceptions import DatabaseNotFoundError


class CustomOrderRepository(ICustomOrderRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, custom_order_id: UUID) -> CustomOrder | None:
        query = (
            "SELECT id, customer_id, dealership_id, model_id, engine_id, transmission_id, "
            "exterior_color, interior_color, status, estimated_price, final_price, notes, "
            "created_at, updated_at FROM get_custom_order_with_details($1::UUID, NULL) LIMIT 1"
        )
        row = await self._db.fetchrow(query, str(custom_order_id))
        if not row:
            return None
        return self._row_to_custom_order(row)

    async def get_by_customer_id(self, customer_id: UUID) -> list[CustomOrder]:
        query = "SELECT * FROM custom_orders WHERE customer_id = $1 ORDER BY created_at DESC"
        rows = await self._db.fetch(query, str(customer_id))
        return [self._row_to_custom_order(row) for row in rows]

    async def get_by_dealership_id(self, dealership_id: int) -> list[CustomOrder]:
        query = (
            "SELECT id, customer_id, dealership_id, model_id, engine_id, transmission_id, "
            "exterior_color, interior_color, status, estimated_price, final_price, notes, "
            "created_at, updated_at FROM get_custom_order_with_details(NULL, $1)"
        )
        rows = await self._db.fetch(query, dealership_id)
        return [self._row_to_custom_order(row) for row in rows]

    async def create(self, custom_order: CustomOrder) -> CustomOrder:
        query = """
            INSERT INTO custom_orders (
                id, customer_id, dealership_id, model_id, engine_id, transmission_id,
                exterior_color, interior_color, status, estimated_price, final_price,
                notes, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(custom_order.id),
            str(custom_order.customer_id),
            custom_order.dealership_id,
            str(custom_order.model_id),
            custom_order.engine_id,
            custom_order.transmission_id,
            custom_order.exterior_color,
            custom_order.interior_color,
            custom_order.status.value,
            float(custom_order.estimated_price) if custom_order.estimated_price else None,
            float(custom_order.final_price) if custom_order.final_price else None,
            custom_order.notes,
            custom_order.created_at or datetime.utcnow(),
        )
        return self._row_to_custom_order(row)

    async def update(self, custom_order: CustomOrder) -> CustomOrder:
        query = """
            UPDATE custom_orders
            SET customer_id = $2, dealership_id = $3, model_id = $4, engine_id = $5,
                transmission_id = $6, exterior_color = $7, interior_color = $8, status = $9,
                estimated_price = $10, final_price = $11, notes = $12, updated_at = $13
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(custom_order.id),
            str(custom_order.customer_id),
            custom_order.dealership_id,
            str(custom_order.model_id),
            custom_order.engine_id,
            custom_order.transmission_id,
            custom_order.exterior_color,
            custom_order.interior_color,
            custom_order.status.value,
            float(custom_order.estimated_price) if custom_order.estimated_price else None,
            float(custom_order.final_price) if custom_order.final_price else None,
            custom_order.notes,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"CustomOrder with id {custom_order.id} not found")
        return self._row_to_custom_order(row)

    async def update_status(self, custom_order_id: UUID, new_status: CustomOrderStatus) -> CustomOrder:
        query = """
            UPDATE custom_orders
            SET status = $2, updated_at = $3
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(query, str(custom_order_id), new_status.value, datetime.utcnow())
        if not row:
            raise DatabaseNotFoundError(f"CustomOrder with id {custom_order_id} not found")
        return self._row_to_custom_order(row)

    async def delete(self, custom_order_id: UUID) -> bool:
        query = "DELETE FROM custom_orders WHERE id = $1"
        result = await self._db.execute(query, str(custom_order_id))
        return result == "DELETE 1"

    def _row_to_custom_order(self, row: asyncpg.Record) -> CustomOrder:
        return CustomOrder(
            id=parse_uuid(row["id"]),
            customer_id=parse_uuid(row["customer_id"]),
            dealership_id=row["dealership_id"],
            model_id=parse_uuid(row["model_id"]),
            engine_id=row["engine_id"],
            transmission_id=row["transmission_id"],
            exterior_color=row["exterior_color"],
            interior_color=row.get("interior_color"),
            status=CustomOrderStatus(row["status"]),
            estimated_price=Decimal(str(row["estimated_price"])) if row.get("estimated_price") else None,
            final_price=Decimal(str(row["final_price"])) if row.get("final_price") else None,
            notes=row.get("notes"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
