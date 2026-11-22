"""Pydantic models for vehicle API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO
from src.domain.value_objects.vehicle_status import VehicleStatus


class VehicleCreateRequest(BaseModel):
    """Request body for creating a vehicle."""

    trim_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    status: VehicleStatus = VehicleStatus.IN_STOCK

    def to_dto(self) -> VehicleCreateDTO:
        """Converts the request to a create DTO."""
        return VehicleCreateDTO(
            trim_id=self.trim_id,
            dealership_id=self.dealership_id,
            vin=self.vin,
            production_year=self.production_year,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            price=self.price,
            status=self.status,
        )


class VehicleUpdateRequest(BaseModel):
    """Request body for updating a vehicle."""

    trim_id: UUID | None = None
    dealership_id: int | None = None
    vin: str | None = None
    production_year: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    price: Decimal | None = None
    status: VehicleStatus | None = None

    def to_dto(self) -> VehicleUpdateDTO:
        """Converts the request to an update DTO."""
        return VehicleUpdateDTO(
            trim_id=self.trim_id,
            dealership_id=self.dealership_id,
            vin=self.vin,
            production_year=self.production_year,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            price=self.price,
            status=self.status,
        )


class VehicleResponse(BaseModel):
    """Single vehicle response model."""

    id: UUID
    model_id: UUID
    trim_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    status: VehicleStatus = VehicleStatus.IN_STOCK
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_name: str | None = None
    trim_name: str | None = None
    images: list[str] | None = None  # photos of this exact vehicle
    model_images: list[str] | None = None  # model appearance, used as fallback

    @classmethod
    def from_dto(cls, vehicle: VehicleDTO) -> "VehicleResponse":
        """Builds the response from a vehicle DTO."""
        return cls(
            id=vehicle.id,
            model_id=vehicle.model_id,
            trim_id=vehicle.trim_id,
            dealership_id=vehicle.dealership_id,
            vin=vehicle.vin,
            production_year=vehicle.production_year,
            exterior_color=vehicle.exterior_color,
            interior_color=vehicle.interior_color,
            price=vehicle.price,
            status=vehicle.status,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            model_name=vehicle.model_name,
            trim_name=vehicle.trim_name,
            images=vehicle.images,
            model_images=vehicle.model_images,
        )


class VehiclesResponse(BaseModel):
    """Paginated vehicles response."""

    vehicles: list[VehicleResponse]
    total: int
