from uuid import UUID

from src.application.abstractions.custom_order_service import ICustomOrderService
from src.application.dtos.custom_order_dto import (
    CustomOrderCreateDTO,
    CustomOrderDTO,
    CustomOrderUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError, ValidationError
from src.application.mappers.custom_order_mapper import CustomOrderMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.custom_order_status import CustomOrderStatus
from src.domain.value_objects.user_role import UserRole


class CustomOrderService(ICustomOrderService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_custom_order(self, create_dto: CustomOrderCreateDTO) -> CustomOrderDTO:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(create_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(create_dto.customer_id))

            model = await uow.model_repository.get_by_id(create_dto.model_id)
            if not model:
                raise NotFoundError("Model", str(create_dto.model_id))

            engine = await uow.engine_repository.get_by_id(create_dto.engine_id)
            if not engine:
                raise NotFoundError("Engine", str(create_dto.engine_id))

            transmission = await uow.transmission_repository.get_by_id(create_dto.transmission_id)
            if not transmission:
                raise NotFoundError("Transmission", str(create_dto.transmission_id))

            dealership = await uow.dealership_repository.get_by_id(create_dto.dealership_id)
            if not dealership:
                raise NotFoundError("Dealership", str(create_dto.dealership_id))

            if create_dto.estimated_price is not None and create_dto.estimated_price < 0:
                raise ValidationError("Estimated price cannot be negative")

            custom_order = CustomOrderMapper.from_create_dto_to_entity(create_dto)
            created_order = await uow.custom_order_repository.create(custom_order)

        return CustomOrderMapper.from_entity_to_dto(created_order)

    async def get_custom_order(self, custom_order_id: UUID) -> CustomOrderDTO:
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))
        return CustomOrderMapper.from_entity_to_dto(custom_order)

    async def get_custom_orders_by_customer(self, customer_id: UUID) -> list[CustomOrderDTO]:
        async with self._uow as uow:
            custom_orders = await uow.custom_order_repository.get_by_customer_id(customer_id)
        return [CustomOrderMapper.from_entity_to_dto(order) for order in custom_orders]

    async def get_custom_orders_by_dealership(self, dealership_id: int) -> list[CustomOrderDTO]:
        async with self._uow as uow:
            custom_orders = await uow.custom_order_repository.get_by_dealership_id(dealership_id)
        return [CustomOrderMapper.from_entity_to_dto(order) for order in custom_orders]

    async def update_custom_order(
        self, custom_order_id: UUID, update_dto: CustomOrderUpdateDTO, current_user_id: UUID | None = None
    ) -> CustomOrderDTO:
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

            if update_dto.model_id:
                model = await uow.model_repository.get_by_id(update_dto.model_id)
                if not model:
                    raise NotFoundError("Model", str(update_dto.model_id))

            if update_dto.engine_id:
                engine = await uow.engine_repository.get_by_id(update_dto.engine_id)
                if not engine:
                    raise NotFoundError("Engine", str(update_dto.engine_id))

            if update_dto.transmission_id:
                transmission = await uow.transmission_repository.get_by_id(update_dto.transmission_id)
                if not transmission:
                    raise NotFoundError("Transmission", str(update_dto.transmission_id))

            if update_dto.estimated_price is not None and update_dto.estimated_price < 0:
                raise ValidationError("Estimated price cannot be negative")
            if update_dto.final_price is not None and update_dto.final_price < 0:
                raise ValidationError("Final price cannot be negative")

            updated_order = CustomOrderMapper.from_update_dto_to_entity(custom_order, update_dto)
            saved_order = await uow.custom_order_repository.update(updated_order)

        return CustomOrderMapper.from_entity_to_dto(saved_order)

    async def update_custom_order_status(
        self, custom_order_id: UUID, new_status: CustomOrderStatus, current_user_id: UUID | None = None
    ) -> CustomOrderDTO:
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
