from uuid import UUID, uuid4

from src.application.dtos.customer_dto import (
    CustomerCreateDTO,
    CustomerDTO,
    CustomerUpdateDTO,
)
from src.domain.entities.customer import Customer


class CustomerMapper:
    """Mapper for converting between Customer DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(customer: Customer) -> CustomerDTO:
        return CustomerDTO(
            id=customer.id,
            user_id=customer.user_id,
            date_of_birth=customer.date_of_birth,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: CustomerCreateDTO, user_id: UUID) -> Customer:
        return Customer(
            id=uuid4(),
            user_id=user_id,
            date_of_birth=create_dto.date_of_birth,
        )

    @staticmethod
    def from_update_dto_to_entity(
        customer: Customer,
        update_dto: CustomerUpdateDTO,
    ) -> Customer:
        return Customer(
            id=customer.id,
            user_id=customer.user_id,
            date_of_birth=update_dto.date_of_birth if update_dto.date_of_birth is not None else customer.date_of_birth,
        )
