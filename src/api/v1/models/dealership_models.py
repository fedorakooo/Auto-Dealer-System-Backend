"""Pydantic models for dealership API."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from src.application.dtos.dealership_dto import (
    DealershipCreateDTO,
    DealershipDTO,
    DealershipUpdateDTO,
)


class DealershipCreateRequest(BaseModel):
    """Request body for creating a dealership."""

    name: str
    address: str
    city_id: int
    phone_number: str | None = None
    email: EmailStr | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True

    def to_dto(self) -> DealershipCreateDTO:
        return DealershipCreateDTO(
            name=self.name,
            address=self.address,
            city_id=self.city_id,
            phone_number=self.phone_number,
            email=str(self.email) if self.email is not None else None,
            opening_hours=self.opening_hours,
            latitude=self.latitude,
            longitude=self.longitude,
            is_active=self.is_active,
        )


class DealershipUpdateRequest(BaseModel):
    """Request body for updating a dealership."""

    name: str | None = None
    address: str | None = None
    city_id: int | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool | None = None

    def to_dto(self) -> DealershipUpdateDTO:
        return DealershipUpdateDTO(
            name=self.name,
            address=self.address,
            city_id=self.city_id,
            phone_number=self.phone_number,
            email=str(self.email) if self.email is not None else None,
            opening_hours=self.opening_hours,
            latitude=self.latitude,
            longitude=self.longitude,
            is_active=self.is_active,
        )


class DealershipResponse(BaseModel):
    """Single dealership response model."""

    id: int
    name: str
    address: str
    city_id: int
    phone_number: str | None = None
    email: EmailStr | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, dealership: DealershipDTO) -> "DealershipResponse":
        return cls(
            id=dealership.id,
            name=dealership.name,
            address=dealership.address,
            city_id=dealership.city_id,
            phone_number=dealership.phone_number,
            email=dealership.email if dealership.email else None,
            opening_hours=dealership.opening_hours,
            latitude=dealership.latitude,
            longitude=dealership.longitude,
            is_active=dealership.is_active,
            updated_at=dealership.updated_at,
        )


class DealershipsResponse(BaseModel):
    """Paginated dealerships response."""

    dealerships: list[DealershipResponse]
    total: int
