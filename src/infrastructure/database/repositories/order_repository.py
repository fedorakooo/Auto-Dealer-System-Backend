import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.order_repository import IOrderRepository
from src.domain.entities.order import Order
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.filters import OrderFilter
from src.domain.value_objects.order_status import OrderStatus
from src.infrastructure.database.exceptions import DatabaseNotFoundError

logger = logging.getLogger(__name__)


class OrderRepository(IOrderRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, order_id: UUID) -> Order | None:
        query = (
            "SELECT id, customer_id, vehicle_id, dealership_id, status, final_price, "
            "created_at, updated_at FROM get_order_with_details($1::UUID, NULL) LIMIT 1"
        )
        row = await self._db.fetchrow(query, str(order_id))
        if not row:
            return None
        return self._row_to_order(row)

    async def get_orders(self, order_filter: OrderFilter) -> tuple[list[Order], int]:
        offset = (order_filter.page - 1) * order_filter.limit

        customer_id_uuid = UUID(order_filter.customer_id) if order_filter.customer_id else None
        status_enum = order_filter.status if order_filter.status else None
        sort_by = order_filter.sort_by.value if order_filter.sort_by else "created_at"
        order_direction = order_filter.order_by.value.upper()

        query = "SELECT * FROM get_orders_filtered($1::UUID, $2, $3::order_status, $4, $5, $6, $7)"

        rows = await self._db.fetch(
            query,
            str(customer_id_uuid) if customer_id_uuid else None,
            order_filter.dealership_id,
            status_enum,
            sort_by,
            order_direction,
            offset,
            order_filter.limit,
        )

        count_query = "SELECT count_orders_filtered($1::UUID, $2, $3::order_status)"

        total = await self._db.fetchval(
            count_query,
            str(customer_id_uuid) if customer_id_uuid else None,
            order_filter.dealership_id,
            status_enum,
        )

        return [self._row_to_order(row) for row in rows], total

    async def get_by_customer_id(self, customer_id: UUID) -> list[Order]:
        query = "SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC"
        rows = await self._db.fetch(query, str(customer_id))
        return [self._row_to_order(row) for row in rows]

    async def get_by_dealership_id(self, dealership_id: int) -> list[Order]:
        query = (
            "SELECT id, customer_id, vehicle_id, dealership_id, status, final_price, "
            "created_at, updated_at FROM get_order_with_details(NULL, $1)"
        )
        rows = await self._db.fetch(query, dealership_id)
        return [self._row_to_order(row) for row in rows]

    async def create(self, order: Order) -> Order:
        query = """
            INSERT INTO orders (id, customer_id, vehicle_id, dealership_id, status, final_price, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(order.id),
            str(order.customer_id),
            str(order.vehicle_id),
            order.dealership_id,
            order.status.value,
            float(order.final_price),
            order.created_at or datetime.utcnow(),
        )
        return self._row_to_order(row)

    async def update(self, order: Order) -> Order:
        query = """
            UPDATE orders
            SET customer_id = $2, vehicle_id = $3, dealership_id = $4, status = $5, final_price = $6, updated_at = $7
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(order.id),
            str(order.customer_id),
            str(order.vehicle_id),
            order.dealership_id,
            order.status.value,
            float(order.final_price),
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"Order with id {order.id} not found")
        return self._row_to_order(row)

    async def update_status(self, order_id: UUID, new_status: OrderStatus) -> bool:
        try:
            logger.info("updating order status")

            await self._db.execute(
                "CALL update_order_status($1::UUID, $2::order_status)",
                str(order_id),
                new_status.value,
            )

            check_query = "SELECT status FROM orders WHERE id = $1::UUID"
            updated_status = await self._db.fetchval(check_query, str(order_id))

            if updated_status and updated_status == new_status.value:
                return True
            return False
        except Exception as exc:
            logger.error(f"Error updating order status: {exc}")
            return False

    async def validate_status_transition(self, old_status: OrderStatus, new_status: OrderStatus) -> bool:
        query = "SELECT is_valid_status_transition($1::order_status, $2::order_status)"
        result = await self._db.fetchval(query, old_status.value, new_status.value)
        return result

    async def delete(self, order_id: UUID) -> bool:
        query = "DELETE FROM orders WHERE id = $1"
        result = await self._db.execute(query, str(order_id))
        return result == "DELETE 1"

    def _row_to_order(self, row: asyncpg.Record) -> Order:
        return Order(
            id=parse_uuid(row["id"]),
            customer_id=parse_uuid(row["customer_id"]),
            vehicle_id=parse_uuid(row["vehicle_id"]),
            dealership_id=row["dealership_id"],
            status=OrderStatus(row["status"]),
            final_price=Decimal(str(row["final_price"])),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
