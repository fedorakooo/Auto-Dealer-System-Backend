from datetime import datetime

from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)
from src.domain.entities.dealership import Dealership


class DealershipMapper:
    """Mapper for converting between Dealership DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(dealership: Dealership) -> DealershipDTO:
        return DealershipDTO(
            id=dealership.id,
            name=dealership.name,
            address=dealership.address,
            city_id=dealership.city_id,
            phone_number=dealership.phone_number,
            email=dealership.email,
            opening_hours=dealership.opening_hours,
            latitude=dealership.latitude,
            longitude=dealership.longitude,
            is_active=dealership.is_active,
            updated_at=dealership.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: DealershipCreateDTO, dealership_id: int) -> Dealership:
        return Dealership(
            id=dealership_id,
            name=create_dto.name,
            address=create_dto.address,
            city_id=create_dto.city_id,
            phone_number=create_dto.phone_number,
            email=create_dto.email,
            opening_hours=create_dto.opening_hours,
            latitude=create_dto.latitude,
            longitude=create_dto.longitude,
            is_active=create_dto.is_active,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        dealership: Dealership,
        update_dto: DealershipUpdateDTO,
    ) -> Dealership:
        return Dealership(
            id=dealership.id,
            name=update_dto.name if update_dto.name is not None else dealership.name,
            address=update_dto.address if update_dto.address is not None else dealership.address,
            city_id=update_dto.city_id if update_dto.city_id is not None else dealership.city_id,
            phone_number=update_dto.phone_number if update_dto.phone_number is not None else dealership.phone_number,
            email=update_dto.email if update_dto.email is not None else dealership.email,
            opening_hours=(
                update_dto.opening_hours if update_dto.opening_hours is not None else dealership.opening_hours
            ),
            latitude=update_dto.latitude if update_dto.latitude is not None else dealership.latitude,
            longitude=update_dto.longitude if update_dto.longitude is not None else dealership.longitude,
            is_active=update_dto.is_active if update_dto.is_active is not None else dealership.is_active,
            updated_at=datetime.utcnow(),
        )
