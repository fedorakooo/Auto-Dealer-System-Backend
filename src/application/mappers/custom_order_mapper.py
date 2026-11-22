from datetime import datetime
from uuid import UUID, uuid4

from src.application.dtos.custom_order_dto import (
    CustomOrderCreateDTO,
    CustomOrderDTO,
    CustomOrderUpdateDTO,
)
from src.domain.entities.custom_order import CustomOrder
from src.domain.value_objects.custom_order_status import CustomOrderStatus


class CustomOrderMapper:
    """Mapper for converting between CustomOrder DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(custom_order: CustomOrder) -> CustomOrderDTO:
        """Maps a custom order entity to a DTO."""
        return CustomOrderDTO(
            id=custom_order.id,
            customer_id=custom_order.customer_id,
            dealership_id=custom_order.dealership_id,
            model_id=custom_order.model_id,
            trim_id=custom_order.trim_id,
            exterior_color=custom_order.exterior_color,
            interior_color=custom_order.interior_color,
            status=custom_order.status,
            estimated_price=custom_order.estimated_price,
            final_price=custom_order.final_price,
            notes=custom_order.notes,
            created_at=custom_order.created_at,
            updated_at=custom_order.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: CustomOrderCreateDTO, model_id: UUID) -> CustomOrder:
        """Builds a new custom order entity from a create DTO."""
        now = datetime.utcnow()
        return CustomOrder(
            id=uuid4(),
            customer_id=create_dto.customer_id,
            dealership_id=create_dto.dealership_id,
            model_id=model_id,
            trim_id=create_dto.trim_id,
            exterior_color=create_dto.exterior_color,
            interior_color=create_dto.interior_color,
            status=CustomOrderStatus.PENDING_APPROVAL,
            estimated_price=create_dto.estimated_price,
            final_price=None,
            notes=create_dto.notes,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        custom_order: CustomOrder,
        update_dto: CustomOrderUpdateDTO,
        model_id: UUID | None = None,
    ) -> CustomOrder:
        """Applies an update DTO to a custom order entity."""
        return CustomOrder(
            id=custom_order.id,
            customer_id=custom_order.customer_id,
            dealership_id=custom_order.dealership_id,
            model_id=model_id if model_id is not None else custom_order.model_id,
            trim_id=update_dto.trim_id if update_dto.trim_id is not None else custom_order.trim_id,
            exterior_color=(
                update_dto.exterior_color if update_dto.exterior_color is not None else custom_order.exterior_color
            ),
            interior_color=(
                update_dto.interior_color if update_dto.interior_color is not None else custom_order.interior_color
            ),
            status=update_dto.status if update_dto.status is not None else custom_order.status,
            estimated_price=(
                update_dto.estimated_price if update_dto.estimated_price is not None else custom_order.estimated_price
            ),
            final_price=update_dto.final_price if update_dto.final_price is not None else custom_order.final_price,
            notes=update_dto.notes if update_dto.notes is not None else custom_order.notes,
            created_at=custom_order.created_at,
            updated_at=datetime.utcnow(),
        )
