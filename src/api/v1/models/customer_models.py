"""Pydantic models for customer API."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.customer_dto import CustomerCreateDTO, CustomerDTO, CustomerUpdateDTO


class CustomerCreateRequest(BaseModel):
    """Request body for creating a customer."""

    first_name: str
    second_name: str
    phone_number: str
    email: str
    password: str
    date_of_birth: date | None = None

    def to_dto(self) -> CustomerCreateDTO:
        return CustomerCreateDTO(
            first_name=self.first_name,
            second_name=self.second_name,
            phone_number=self.phone_number,
            email=self.email,
            password=self.password,
            date_of_birth=self.date_of_birth,
        )


class CustomerUpdateRequest(BaseModel):
    """Request body for updating a customer."""

    date_of_birth: date | None = None

    def to_dto(self) -> CustomerUpdateDTO:
        return CustomerUpdateDTO(
            date_of_birth=self.date_of_birth,
        )


class CustomerResponse(BaseModel):
    """Single customer response model."""

    id: UUID
    user_id: UUID
    date_of_birth: date | None = None

    @classmethod
    def from_dto(cls, customer: CustomerDTO) -> "CustomerResponse":
        return cls(
            id=customer.id,
            user_id=customer.user_id,
            date_of_birth=customer.date_of_birth,
        )


class CustomersResponse(BaseModel):
    """List of customers response."""

    customers: list[CustomerResponse]
