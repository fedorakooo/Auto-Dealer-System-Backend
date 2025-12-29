"""Pydantic models for vehicle API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.vehicle_dto import VehicleCreateDTO, VehicleDTO, VehicleUpdateDTO


class VehicleCreateRequest(BaseModel):
    """Request body for creating a vehicle."""

    model_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    is_active: bool = True

    def to_dto(self) -> VehicleCreateDTO:
        return VehicleCreateDTO(
            model_id=self.model_id,
            dealership_id=self.dealership_id,
            vin=self.vin,
            production_year=self.production_year,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            price=self.price,
            is_active=self.is_active,
        )


class VehicleUpdateRequest(BaseModel):
    """Request body for updating a vehicle."""

    model_id: UUID | None = None
    dealership_id: int | None = None
    vin: str | None = None
    production_year: int | None = None
    exterior_color: str | None = None
    interior_color: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None

    def to_dto(self) -> VehicleUpdateDTO:
        return VehicleUpdateDTO(
            model_id=self.model_id,
            dealership_id=self.dealership_id,
            vin=self.vin,
            production_year=self.production_year,
            exterior_color=self.exterior_color,
            interior_color=self.interior_color,
            price=self.price,
            is_active=self.is_active,
        )


class VehicleResponse(BaseModel):
    """Single vehicle response model."""

    id: UUID
    model_id: UUID
    dealership_id: int
    vin: str
    production_year: int
    exterior_color: str
    interior_color: str | None = None
    price: Decimal = Decimal("0.00")
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_name: str | None = None
    images: list[str] | None = None  # URLs to model media images

    @classmethod
    def from_dto(cls, vehicle: VehicleDTO) -> "VehicleResponse":
        return cls(
            id=vehicle.id,
            model_id=vehicle.model_id,
            dealership_id=vehicle.dealership_id,
            vin=vehicle.vin,
            production_year=vehicle.production_year,
            exterior_color=vehicle.exterior_color,
            interior_color=vehicle.interior_color,
            price=vehicle.price,
            is_active=vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            model_name=vehicle.model_name,
            images=vehicle.images,
        )


class VehiclesResponse(BaseModel):
    """Paginated vehicles response."""

    vehicles: list[VehicleResponse]
    total: int
