import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.operations_repository import IOperationsRepository


def _dict(row: Any) -> dict[str, Any]:
    return dict(row)


class OperationsRepository(IOperationsRepository):
    def __init__(self, db: IDatabaseConnection):
        self._db = db

    async def vehicle_history(self, vehicle_id: UUID, kind: str, limit: int) -> list[dict[str, Any]]:
        queries = {
            "price": """
                SELECT id, vehicle_id, price, valid_from, valid_to, changed_by_user_id
                FROM vehicle_price_history WHERE vehicle_id = $1
                ORDER BY valid_from DESC, id DESC LIMIT $2
            """,
            "status": """
                SELECT id, vehicle_id, status, reason, changed_by_user_id, changed_at
                FROM vehicle_status_history WHERE vehicle_id = $1
                ORDER BY changed_at DESC, id DESC LIMIT $2
            """,
        }
        return [_dict(row) for row in await self._db.fetch(queries[kind], vehicle_id, limit)]

    async def add_vehicle_status(
        self, vehicle_id: UUID, status: str, reason: str | None, user_id: UUID
    ) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO vehicle_status_history(vehicle_id, status, reason, changed_by_user_id)
            VALUES ($1, $2::vehicle_lifecycle_status, $3, $4)
            RETURNING id, vehicle_id, status, reason, changed_by_user_id, changed_at
            """,
            vehicle_id,
            status,
            reason,
            user_id,
        )
        return _dict(row)

    async def order_history(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch(
            """
            SELECT id, order_id, from_status, to_status, changed_by_user_id, comment, changed_at
            FROM order_status_history WHERE order_id = $1
            ORDER BY changed_at DESC, id DESC LIMIT $2
            """,
            order_id,
            limit,
        )
        return [_dict(row) for row in rows]

    async def payments(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch(
            """
            SELECT id, order_id, amount, method, status, external_reference, paid_at, created_at, updated_at
            FROM order_payments WHERE order_id = $1 ORDER BY created_at DESC, id DESC LIMIT $2
            """,
            order_id,
            limit,
        )
        return [_dict(row) for row in rows]

    async def create_payment(
        self, order_id: UUID, amount: Decimal, method: str, status: str, external_reference: str | None
    ) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO order_payments(order_id, amount, method, status, external_reference, paid_at)
            VALUES ($1, $2, $3::payment_method, $4::payment_status, $5,
                    CASE WHEN $4 = 'paid' THEN now() ELSE NULL END)
            RETURNING id, order_id, amount, method, status, external_reference, paid_at, created_at, updated_at
            """,
            order_id,
            amount,
            method,
            status,
            external_reference,
        )
        if status in {"authorized", "paid"}:
            await self._db.execute(
                """
                UPDATE orders o SET status = 'processing'
                WHERE o.id = $1 AND o.status = 'pending_payment'
                  AND (SELECT COALESCE(SUM(p.amount), 0) FROM order_payments p
                       WHERE p.order_id = o.id AND p.status IN ('authorized', 'paid')) >= o.final_price
                """,
                order_id,
            )
        return _dict(row)

    async def addresses(self, customer_id: UUID) -> list[dict[str, Any]]:
        rows = await self._db.fetch(
            "SELECT * FROM customer_addresses WHERE customer_id = $1 ORDER BY is_default DESC, created_at", customer_id
        )
        return [_dict(row) for row in rows]

    async def create_address(self, customer_id: UUID, values: dict[str, Any]) -> dict[str, Any]:
        if values["is_default"]:
            await self._db.execute(
                "UPDATE customer_addresses SET is_default = false WHERE customer_id = $1", customer_id
            )
        row = await self._db.fetchrow(
            """
            INSERT INTO customer_addresses(
                customer_id, label, country, city, address_line_1, address_line_2, postal_code, is_default
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            customer_id,
            values["label"],
            values["country"],
            values["city"],
            values["address_line_1"],
            values.get("address_line_2"),
            values.get("postal_code"),
            values["is_default"],
        )
        return _dict(row)

    async def delete_address(self, customer_id: UUID, address_id: UUID) -> bool:
        result = await self._db.execute(
            "DELETE FROM customer_addresses WHERE id = $1 AND customer_id = $2", address_id, customer_id
        )
        return result == "DELETE 1"

    async def update_address(
        self, customer_id: UUID, address_id: UUID, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        if values["is_default"]:
            await self._db.execute(
                "UPDATE customer_addresses SET is_default = false WHERE customer_id = $1", customer_id
            )
        row = await self._db.fetchrow(
            """
            UPDATE customer_addresses SET
                label = $3, country = $4, city = $5, address_line_1 = $6,
                address_line_2 = $7, postal_code = $8, is_default = $9
            WHERE id = $1 AND customer_id = $2 RETURNING *
            """,
            address_id,
            customer_id,
            values["label"],
            values["country"],
            values["city"],
            values["address_line_1"],
            values.get("address_line_2"),
            values.get("postal_code"),
            values["is_default"],
        )
        return _dict(row) if row else None

    async def employee_profiles(self, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch("SELECT * FROM employee_profiles ORDER BY created_at DESC LIMIT $1", limit)
        return [_dict(row) for row in rows]

    async def create_employee_profile(self, values: dict[str, Any]) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO employee_profiles(user_id, dealership_id, position, hire_date, status)
            VALUES ($1, $2, $3, $4, $5::employment_status) RETURNING *
            """,
            values["user_id"],
            values["dealership_id"],
            values["position"],
            values["hire_date"],
            values["status"],
        )
        return _dict(row)

    async def service_catalog(self, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch("SELECT * FROM service_catalog WHERE is_active ORDER BY name LIMIT $1", limit)
        return [_dict(row) for row in rows]

    async def create_appointment(
        self,
        customer_id: UUID,
        dealership_id: int,
        vehicle_id: UUID | None,
        requested_datetime: datetime,
        notes: str | None,
    ) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO service_appointments(customer_id, dealership_id, vehicle_id, requested_datetime, notes)
            VALUES ($1, $2, $3, $4, $5) RETURNING *
            """,
            customer_id,
            dealership_id,
            vehicle_id,
            requested_datetime,
            notes,
        )
        return _dict(row)

    async def appointments(self, customer_id: UUID | None, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch(
            """
            SELECT * FROM service_appointments
            WHERE ($1::uuid IS NULL OR customer_id = $1)
            ORDER BY requested_datetime DESC LIMIT $2
            """,
            customer_id,
            limit,
        )
        return [_dict(row) for row in rows]

    async def change_appointment_status(self, appointment_id: UUID, status: str) -> dict[str, Any] | None:
        row = await self._db.fetchrow(
            """
            UPDATE service_appointments SET status = $2::service_appointment_status
            WHERE id = $1 RETURNING *
            """,
            appointment_id,
            status,
        )
        return _dict(row) if row else None

    async def delete_appointment(self, appointment_id: UUID, customer_id: UUID) -> bool:
        result = await self._db.execute(
            """
            DELETE FROM service_appointments
            WHERE id = $1 AND customer_id = $2 AND status = 'requested'
            """,
            appointment_id,
            customer_id,
        )
        return result == "DELETE 1"

    async def create_service_order(self, values: dict[str, Any]) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO service_orders(
                appointment_id, customer_id, dealership_id, vehicle_id, assigned_employee_id, odometer_km
            ) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
            """,
            values.get("appointment_id"),
            values["customer_id"],
            values["dealership_id"],
            values["vehicle_id"],
            values.get("assigned_employee_id"),
            values.get("odometer_km"),
        )
        return _dict(row)

    async def add_service_item(self, service_order_id: UUID, values: dict[str, Any]) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            INSERT INTO service_order_items(service_order_id, service_id, description, quantity, unit_price)
            VALUES ($1, $2, $3, $4, $5) RETURNING *
            """,
            service_order_id,
            values.get("service_id"),
            values["description"],
            values["quantity"],
            values["unit_price"],
        )
        return _dict(row)

    async def change_service_order_status(self, service_order_id: UUID, status: str) -> dict[str, Any]:
        row = await self._db.fetchrow(
            """
            UPDATE service_orders SET status = $2::service_order_status,
                closed_at = CASE WHEN $2 = 'completed' THEN now() ELSE closed_at END
            WHERE id = $1 AND ($2 <> 'completed' OR status = 'in_progress') RETURNING *
            """,
            service_order_id,
            status,
        )
        if row is None:
            raise ValueError("service order not found or cannot be completed from current status")
        return _dict(row)

    async def service_orders(self, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch("SELECT * FROM service_orders ORDER BY opened_at DESC LIMIT $1", limit)
        return [_dict(row) for row in rows]

    async def spare_parts(self, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch("SELECT * FROM spare_parts WHERE is_active ORDER BY name LIMIT $1", limit)
        return [_dict(row) for row in rows]

    async def inventory(self, dealership_id: int, below_reorder: bool, limit: int) -> list[dict[str, Any]]:
        rows = await self._db.fetch(
            """
            SELECT i.dealership_id, i.part_id, p.sku, p.name, p.unit_price,
                   i.quantity, i.reserved_quantity, i.reorder_level, i.updated_at
            FROM dealership_part_inventory i JOIN spare_parts p ON p.id = i.part_id
            WHERE i.dealership_id = $1 AND (NOT $2 OR i.quantity - i.reserved_quantity <= i.reorder_level)
            ORDER BY p.name LIMIT $3
            """,
            dealership_id,
            below_reorder,
            limit,
        )
        return [_dict(row) for row in rows]

    async def reserve_part(self, dealership_id: int, part_id: UUID, quantity: int) -> dict[str, Any]:
        await self._db.fetchrow(
            "SELECT part_id FROM dealership_part_inventory WHERE dealership_id = $1 AND part_id = $2 FOR UPDATE",
            dealership_id,
            part_id,
        )
        row = await self._db.fetchrow(
            """
            UPDATE dealership_part_inventory
            SET reserved_quantity = reserved_quantity + $3
            WHERE dealership_id = $1 AND part_id = $2
              AND quantity - reserved_quantity >= $3
            RETURNING dealership_id, part_id, quantity, reserved_quantity, reorder_level, updated_at
            """,
            dealership_id,
            part_id,
            quantity,
        )
        if row is None:
            raise ValueError("part not found or insufficient available quantity")
        return _dict(row)

    async def idempotency(self, key: str) -> dict[str, Any] | None:
        await self._db.execute("SELECT pg_advisory_xact_lock(hashtext($1))", key)
        row = await self._db.fetchrow(
            "SELECT * FROM idempotency_keys WHERE idempotency_key = $1 AND expires_at > now() FOR UPDATE", key
        )
        return _dict(row) if row else None

    async def save_idempotency(
        self,
        key: str,
        user_id: UUID,
        method: str,
        path: str,
        request_hash: str,
        response_status: int,
        response_body: dict[str, Any],
    ) -> None:
        await self._db.execute(
            """
            INSERT INTO idempotency_keys(
                user_id, idempotency_key, request_method, request_path, request_hash,
                response_status, response_body, expires_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, now() + interval '24 hours')
            """,
            user_id,
            key,
            method,
            path,
            request_hash,
            response_status,
            json.dumps(response_body, default=str),
        )

    async def add_outbox(
        self, aggregate_type: str, aggregate_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        await self._db.execute(
            """
            INSERT INTO outbox_events(aggregate_type, aggregate_id, event_type, payload)
            VALUES ($1, $2, $3, $4::jsonb)
            """,
            aggregate_type,
            aggregate_id,
            event_type,
            json.dumps(payload, default=str),
        )
