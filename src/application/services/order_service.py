from uuid import UUID

from src.application.abstractions.order_service import IOrderService
from src.application.dtos.order_dto import OrderCreateDTO, OrderDTO, OrderUpdateDTO
from src.application.exceptions.errors import (
    BusinessError,
    NotFoundError,
    PermissionError,
    ValidationError,
)
from src.application.mappers.order_mapper import OrderMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.exceptions.vehicle_errors import VehicleAlreadyOrderedError
from src.domain.value_objects.filters import OrderFilter
from src.domain.value_objects.order_status import OrderStatus
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.vehicle_status import VehicleStatus


class OrderService(IOrderService):
    """Service for order operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def _with_model_ids(self, dtos: list[OrderDTO]) -> list[OrderDTO]:
        """Attach each vehicle's model so clients can build /models/{model_id}/vehicles/{vehicle_id} links."""
        async with self._uow as uow:
            model_ids = await uow.vehicle_repository.get_model_ids(list({dto.vehicle_id for dto in dtos}))
        for dto in dtos:
            dto.model_id = model_ids.get(dto.vehicle_id)
        return dtos

    async def create_order(self, create_dto: OrderCreateDTO) -> OrderDTO:
        """Create a new order."""
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(create_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(create_dto.customer_id))

            vehicle = await uow.vehicle_repository.get_by_id(create_dto.vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(create_dto.vehicle_id))

            if vehicle.status == VehicleStatus.RESERVED:
                raise BusinessError("Vehicle is already reserved in another active order")
            if vehicle.status != VehicleStatus.IN_STOCK:
                raise BusinessError("Vehicle is not available for purchase")

            if vehicle.dealership_id != create_dto.dealership_id:
                raise ValidationError("Dealership ID does not match vehicle's dealership")

            dealership = await uow.dealership_repository.get_by_id(create_dto.dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(create_dto.dealership_id))

            if create_dto.final_price < 0:
                raise ValidationError("Price cannot be negative")

            final_price = create_dto.final_price if create_dto.final_price > 0 else vehicle.price

            order_dto = OrderCreateDTO(
                customer_id=create_dto.customer_id,
                vehicle_id=create_dto.vehicle_id,
                dealership_id=create_dto.dealership_id,
                final_price=final_price,
            )

            order = OrderMapper.from_create_dto_to_entity(order_dto)
            try:
                created_order = await uow.order_repository.create(order)
            except VehicleAlreadyOrderedError as exc:
                raise BusinessError("Vehicle is already reserved in another active order") from exc

        return (await self._with_model_ids([OrderMapper.from_entity_to_dto(created_order)]))[0]

    async def get_order(self, order_id: UUID) -> OrderDTO:
        """Get order by ID."""
        async with self._uow as uow:
            order = await uow.order_repository.get_by_id(order_id)
            if not order:
                raise NotFoundError("Order", str(order_id))
        return (await self._with_model_ids([OrderMapper.from_entity_to_dto(order)]))[0]

    async def get_orders(self, order_filter: OrderFilter) -> tuple[list[OrderDTO], int]:
        """Get orders with filtering and pagination."""
        async with self._uow as uow:
            orders, total = await uow.order_repository.get_orders(order_filter)
        return await self._with_model_ids([OrderMapper.from_entity_to_dto(order) for order in orders]), total

    async def get_orders_by_customer(self, customer_id: UUID) -> list[OrderDTO]:
        """Get orders by customer ID."""
        async with self._uow as uow:
            orders = await uow.order_repository.get_by_customer_id(customer_id)
        return await self._with_model_ids([OrderMapper.from_entity_to_dto(order) for order in orders])

    async def get_orders_by_dealership(self, dealership_id: int) -> list[OrderDTO]:
        """Get orders by dealership ID."""
        async with self._uow as uow:
            orders = await uow.order_repository.get_by_dealership_id(dealership_id)
        return await self._with_model_ids([OrderMapper.from_entity_to_dto(order) for order in orders])

    async def update_order(
        self, order_id: UUID, update_dto: OrderUpdateDTO, current_user_id: UUID | None = None
    ) -> OrderDTO:
        """Update order."""
        async with self._uow as uow:
            order = await uow.order_repository.get_by_id(order_id)
            if not order:
                raise NotFoundError("Order", str(order_id))

            if update_dto.final_price is not None and update_dto.final_price <= 0:
                raise ValidationError("Price must be positive")

            updated_order = OrderMapper.from_update_dto_to_entity(order, update_dto)
            saved_order = await uow.order_repository.update(updated_order)

        return (await self._with_model_ids([OrderMapper.from_entity_to_dto(saved_order)]))[0]

    async def update_order_status(
        self, order_id: UUID, new_status: OrderStatus, current_user_id: UUID | None = None
    ) -> OrderDTO:
        """Update order status."""
        async with self._uow as uow:
            order = await uow.order_repository.get_by_id(order_id)
            if not order:
                raise NotFoundError("Order", str(order_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    raise BusinessError("Only ADMIN and EMPLOYEE can update order status")

            is_valid = await uow.order_repository.validate_status_transition(order.status, new_status)
            if not is_valid:
                raise BusinessError(f"Invalid status transition from {order.status.value} to {new_status.value}")

            await uow.order_repository.update_status(order_id, new_status, current_user_id)

            updated_order = await uow.order_repository.get_by_id(order_id)
            if not updated_order:
                raise NotFoundError("Order", str(order_id))
        return (await self._with_model_ids([OrderMapper.from_entity_to_dto(updated_order)]))[0]

    async def delete_order(self, order_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete order."""
        async with self._uow as uow:
            order = await uow.order_repository.get_by_id(order_id)
            if not order:
                raise NotFoundError("Order", str(order_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))

                # Admins may delete any order; employees too; customers only their own unpaid ones.
                if current_user.role != UserRole.ADMIN:
                    if current_user.role == UserRole.CUSTOMER:
                        customer = await uow.customer_repository.get_by_user_id(current_user_id)
                        if not customer or customer.id != order.customer_id:
                            raise PermissionError("You can only delete your own orders")
                        if order.status != OrderStatus.PENDING_PAYMENT:
                            raise BusinessError("You can only delete orders with pending payment status")
                    elif current_user.role != UserRole.EMPLOYEE:
                        raise PermissionError("You don't have permission to delete orders")

            result = await uow.order_repository.delete(order_id)
        return result
