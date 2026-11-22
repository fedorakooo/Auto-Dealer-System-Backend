"""Pydantic models for dealership API."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

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
    description: str | None = Field(None, max_length=5000)

    def to_dto(self) -> DealershipCreateDTO:
        """Converts the request to a create DTO."""
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
            description=self.description,
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
    description: str | None = Field(None, max_length=5000, description="Blank text clears the description")

    def to_dto(self) -> DealershipUpdateDTO:
        """Converts the request to an update DTO."""
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
            description=self.description,
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
    description: str | None = None
    updated_at: datetime | None = None
    rating_average: Decimal | None = None
    reviews_count: int = 0
    cover_url: str | None = None

    @classmethod
    def from_dto(cls, dealership: DealershipDTO) -> "DealershipResponse":
        """Builds the response from a dealership DTO."""
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
            description=dealership.description,
            updated_at=dealership.updated_at,
            rating_average=dealership.rating_average,
            reviews_count=dealership.reviews_count,
            cover_url=(
                f"/api/v1/dealerships/{dealership.id}/media/{dealership.cover_media_id}/file"
                if dealership.cover_media_id
                else None
            ),
        )


class DealershipsResponse(BaseModel):
    """Paginated dealerships response."""

    dealerships: list[DealershipResponse]
    total: int
