import hashlib
import json
from typing import Any
from uuid import UUID

from src.application.abstractions.operations_service import IOperationsService
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.domain.abstractions.database.uow import IUnitOfWork


class OperationsService(IOperationsService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def _customer_id(self, user_id: UUID) -> UUID:
        customer = await self._uow.customer_repository.get_by_user_id(user_id)
        if customer is None:
            raise NotFoundError("Customer for user", str(user_id))
        return customer.id

    @staticmethod
    def _hash(body: dict[str, Any]) -> str:
        encoded = json.dumps(body, sort_keys=True, default=str, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    async def vehicle_history(self, vehicle_id: UUID, kind: str, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.vehicle_history(vehicle_id, kind, limit)

    async def add_vehicle_status(
        self, vehicle_id: UUID, status: str, reason: str | None, user_id: UUID
    ) -> dict[str, Any]:
        async with self._uow:
            result = await self._uow.operations_repository.add_vehicle_status(vehicle_id, status, reason, user_id)
            await self._uow.operations_repository.add_outbox(
                "vehicle", str(vehicle_id), "vehicle.status_changed", result
            )
            return result

    async def order_history(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.order_history(order_id, limit)

    async def payments(self, order_id: UUID, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.payments(order_id, limit)

    async def create_payment(self, order_id: UUID, body: dict[str, Any], key: str, user_id: UUID) -> dict[str, Any]:
        request_hash = self._hash(body)
        path = f"/api/v1/orders/{order_id}/payments"
        async with self._uow:
            saved = await self._uow.operations_repository.idempotency(key)
            if saved:
                if saved["request_hash"] != request_hash or saved["request_path"] != path:
                    raise BusinessError("Idempotency-Key was already used for a different request")
                return saved["response_body"]
            result = await self._uow.operations_repository.create_payment(
                order_id, body["amount"], body["method"], body["status"], body.get("external_reference")
            )
            await self._uow.operations_repository.add_outbox("order", str(order_id), "order.payment_registered", result)
            await self._uow.operations_repository.save_idempotency(
                key, user_id, "POST", path, request_hash, 201, result
            )
            return result

    async def addresses(self, user_id: UUID) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.addresses(await self._customer_id(user_id))

    async def create_address(self, user_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        async with self._uow:
            customer_id = await self._customer_id(user_id)
            return await self._uow.operations_repository.create_address(customer_id, body)

    async def delete_address(self, user_id: UUID, address_id: UUID) -> None:
        async with self._uow:
            customer_id = await self._customer_id(user_id)
            if not await self._uow.operations_repository.delete_address(customer_id, address_id):
                raise NotFoundError("Address", str(address_id))

    async def update_address(self, user_id: UUID, address_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        async with self._uow:
            customer_id = await self._customer_id(user_id)
            result = await self._uow.operations_repository.update_address(customer_id, address_id, body)
            if result is None:
                raise NotFoundError("Address", str(address_id))
            return result

    async def employee_profiles(self, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.employee_profiles(limit)

    async def create_employee_profile(self, body: dict[str, Any]) -> dict[str, Any]:
        async with self._uow:
            return await self._uow.operations_repository.create_employee_profile(body)

    async def catalog(self, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.service_catalog(limit)

    async def create_appointment(self, user_id: UUID, body: dict[str, Any], key: str) -> dict[str, Any]:
        request_hash = self._hash(body)
        path = "/api/v1/service/appointments"
        async with self._uow:
            saved = await self._uow.operations_repository.idempotency(key)
            if saved:
                if saved["request_hash"] != request_hash or saved["request_path"] != path:
                    raise BusinessError("Idempotency-Key was already used for a different request")
                return saved["response_body"]
            customer_id = await self._customer_id(user_id)
            result = await self._uow.operations_repository.create_appointment(
                customer_id,
                body["dealership_id"],
                body.get("vehicle_id"),
                body["requested_datetime"],
                body.get("notes"),
            )
            await self._uow.operations_repository.add_outbox(
                "service_appointment", str(result["id"]), "service.appointment_requested", result
            )
            await self._uow.operations_repository.save_idempotency(
                key, user_id, "POST", path, request_hash, 201, result
            )
            return result

    async def appointments(self, user_id: UUID | None, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            customer_id = await self._customer_id(user_id) if user_id else None
            return await self._uow.operations_repository.appointments(customer_id, limit)

    async def change_appointment_status(self, appointment_id: UUID, status: str) -> dict[str, Any]:
        async with self._uow:
            result = await self._uow.operations_repository.change_appointment_status(appointment_id, status)
            if result is None:
                raise NotFoundError("Service appointment", str(appointment_id))
            await self._uow.operations_repository.add_outbox(
                "service_appointment", str(appointment_id), "service.appointment_status_changed", result
            )
            return result

    async def delete_appointment(self, user_id: UUID, appointment_id: UUID) -> None:
        async with self._uow:
            customer_id = await self._customer_id(user_id)
            if not await self._uow.operations_repository.delete_appointment(appointment_id, customer_id):
                raise BusinessError("Only an owned appointment in requested status can be deleted")

    async def create_service_order(self, body: dict[str, Any]) -> dict[str, Any]:
        async with self._uow:
            result = await self._uow.operations_repository.create_service_order(body)
            await self._uow.operations_repository.add_outbox(
                "service_order", str(result["id"]), "service.order_opened", result
            )
            return result

    async def add_service_item(self, order_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        async with self._uow:
            return await self._uow.operations_repository.add_service_item(order_id, body)

    async def change_service_status(self, order_id: UUID, status: str) -> dict[str, Any]:
        async with self._uow:
            try:
                result = await self._uow.operations_repository.change_service_order_status(order_id, status)
            except ValueError as exc:
                raise BusinessError(str(exc)) from exc
            await self._uow.operations_repository.add_outbox(
                "service_order", str(order_id), "service.order_status_changed", result
            )
            return result

    async def service_orders(self, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.service_orders(limit)

    async def spare_parts(self, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.spare_parts(limit)

    async def inventory(self, dealership_id: int, below_reorder: bool, limit: int) -> list[dict[str, Any]]:
        async with self._uow:
            return await self._uow.operations_repository.inventory(dealership_id, below_reorder, limit)

    async def reserve_part(self, dealership_id: int, part_id: UUID, quantity: int) -> dict[str, Any]:
        async with self._uow:
            try:
                result = await self._uow.operations_repository.reserve_part(dealership_id, part_id, quantity)
            except ValueError as exc:
                raise BusinessError(str(exc)) from exc
            await self._uow.operations_repository.add_outbox(
                "inventory", f"{dealership_id}:{part_id}", "inventory.part_reserved", result
            )
            return result
