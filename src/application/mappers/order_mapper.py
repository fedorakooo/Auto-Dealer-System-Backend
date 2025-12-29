from datetime import datetime
from uuid import uuid4

from src.application.dtos.order_dto import OrderCreateDTO, OrderDTO, OrderUpdateDTO
from src.domain.entities.order import Order
from src.domain.value_objects.order_status import OrderStatus


class OrderMapper:
    """Mapper for converting between Order DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(order: Order) -> OrderDTO:
        return OrderDTO(
            id=order.id,
            customer_id=order.customer_id,
            vehicle_id=order.vehicle_id,
            dealership_id=order.dealership_id,
            status=order.status,
            final_price=order.final_price,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: OrderCreateDTO) -> Order:
        now = datetime.utcnow()
        return Order(
            id=uuid4(),
            customer_id=create_dto.customer_id,
            vehicle_id=create_dto.vehicle_id,
            dealership_id=create_dto.dealership_id,
            status=OrderStatus.PENDING_PAYMENT,
            final_price=create_dto.final_price,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        order: Order,
        update_dto: OrderUpdateDTO,
    ) -> Order:
        return Order(
            id=order.id,
            customer_id=order.customer_id,
            vehicle_id=update_dto.vehicle_id if update_dto.vehicle_id is not None else order.vehicle_id,
            dealership_id=update_dto.dealership_id if update_dto.dealership_id is not None else order.dealership_id,
            status=update_dto.status if update_dto.status is not None else order.status,
            final_price=update_dto.final_price if update_dto.final_price is not None else order.final_price,
            created_at=order.created_at,
            updated_at=datetime.utcnow(),
        )
