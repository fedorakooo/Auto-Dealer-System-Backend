from uuid import UUID

from src.application.abstractions.custom_order_service import ICustomOrderService
from src.application.dtos.custom_order_dto import (
    CustomOrderCreateDTO,
    CustomOrderDTO,
    CustomOrderUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError, PermissionError, ValidationError
from src.application.mappers.custom_order_mapper import CustomOrderMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.custom_order_status import CustomOrderStatus
from src.domain.value_objects.user_role import UserRole


class CustomOrderService(ICustomOrderService):
    """Service for custom order operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def create_custom_order(self, create_dto: CustomOrderCreateDTO) -> CustomOrderDTO:
        """Create a new custom order."""
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(create_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(create_dto.customer_id))

            trim = await uow.trim_repository.get_by_id(create_dto.trim_id)
            if not trim:
                raise NotFoundError("Trim", str(create_dto.trim_id))

            dealership = await uow.dealership_repository.get_by_id(create_dto.dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(create_dto.dealership_id))

            if create_dto.estimated_price is not None and create_dto.estimated_price < 0:
                raise ValidationError("Estimated price cannot be negative")

            custom_order = CustomOrderMapper.from_create_dto_to_entity(create_dto, trim.model_id)
            created_order = await uow.custom_order_repository.create(custom_order)

        return CustomOrderMapper.from_entity_to_dto(created_order)

    async def get_custom_order(self, custom_order_id: UUID) -> CustomOrderDTO:
        """Get custom order by ID."""
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))
        return CustomOrderMapper.from_entity_to_dto(custom_order)

    async def get_custom_orders_by_customer(self, customer_id: UUID) -> list[CustomOrderDTO]:
        """Get custom orders by customer ID."""
        async with self._uow as uow:
            custom_orders = await uow.custom_order_repository.get_by_customer_id(customer_id)
        return [CustomOrderMapper.from_entity_to_dto(order) for order in custom_orders]

    async def get_custom_orders_by_dealership(self, dealership_id: int) -> list[CustomOrderDTO]:
        """Get custom orders by dealership ID."""
        async with self._uow as uow:
            custom_orders = await uow.custom_order_repository.get_by_dealership_id(dealership_id)
        return [CustomOrderMapper.from_entity_to_dto(order) for order in custom_orders]

    async def update_custom_order(
        self, custom_order_id: UUID, update_dto: CustomOrderUpdateDTO, current_user_id: UUID | None = None
    ) -> CustomOrderDTO:
        """Update custom order."""
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    customer = await uow.customer_repository.get_by_user_id(current_user_id)
                    if not customer or customer.id != custom_order.customer_id:
                        raise PermissionError("You can only update your own custom orders")
                    if custom_order.status != CustomOrderStatus.PENDING_APPROVAL:
                        raise PermissionError("You can only update custom orders with PENDING_APPROVAL status")

            new_model_id = None
            if update_dto.trim_id:
                trim = await uow.trim_repository.get_by_id(update_dto.trim_id)
                if not trim:
                    raise NotFoundError("Trim", str(update_dto.trim_id))
                new_model_id = trim.model_id

            if update_dto.estimated_price is not None and update_dto.estimated_price < 0:
                raise ValidationError("Estimated price cannot be negative")
            if update_dto.final_price is not None and update_dto.final_price < 0:
                raise ValidationError("Final price cannot be negative")

            updated_order = CustomOrderMapper.from_update_dto_to_entity(custom_order, update_dto, new_model_id)
            saved_order = await uow.custom_order_repository.update(updated_order)

        return CustomOrderMapper.from_entity_to_dto(saved_order)

    async def update_custom_order_status(
        self, custom_order_id: UUID, new_status: CustomOrderStatus, current_user_id: UUID | None = None
    ) -> CustomOrderDTO:
        """Update custom order status."""
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    raise PermissionError("Only employees and admins can change custom order status")

            updated_order = await uow.custom_order_repository.update_status(custom_order_id, new_status)

        return CustomOrderMapper.from_entity_to_dto(updated_order)

    async def delete_custom_order(self, custom_order_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete custom order."""
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    customer = await uow.customer_repository.get_by_user_id(current_user_id)
                    if not customer or customer.id != custom_order.customer_id:
                        raise PermissionError("You can only delete your own custom orders")
                    if custom_order.status != CustomOrderStatus.PENDING_APPROVAL:
                        raise PermissionError("You can only delete custom orders with PENDING_APPROVAL status")

            result = await uow.custom_order_repository.delete(custom_order_id)
        return result
