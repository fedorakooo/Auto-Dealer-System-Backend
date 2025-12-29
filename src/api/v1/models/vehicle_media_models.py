"""Pydantic models for vehicle media API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.vehicle_media_dto import (
    VehicleMediaCreateDTO,
    VehicleMediaDTO,
    VehicleMediaUpdateDTO,
)
from src.domain.value_objects.media_type import MediaType


class VehicleMediaCreateRequest(BaseModel):
    """Request body for creating vehicle media."""

    vehicle_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0

    def to_dto(self) -> VehicleMediaCreateDTO:
        return VehicleMediaCreateDTO(
            vehicle_id=self.vehicle_id,
            url=self.url,
            media_type=self.media_type,
            description=self.description,
            sort_order=self.sort_order,
        )


class VehicleMediaUpdateRequest(BaseModel):
    """Request body for updating vehicle media."""

    url: str | None = None
    media_type: MediaType | None = None
    description: str | None = None
    sort_order: int | None = None

    def to_dto(self) -> VehicleMediaUpdateDTO:
        return VehicleMediaUpdateDTO(
            url=self.url,
            media_type=self.media_type,
            description=self.description,
            sort_order=self.sort_order,
        )


class VehicleMediaResponse(BaseModel):
    """Single vehicle media response model."""

    id: UUID
    vehicle_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, media: VehicleMediaDTO) -> "VehicleMediaResponse":
        return cls(
            id=media.id,
            vehicle_id=media.vehicle_id,
            url=media.url,
            media_type=media.media_type,
            description=media.description,
            sort_order=media.sort_order,
            updated_at=media.updated_at,
        )


class VehicleMediaListResponse(BaseModel):
    """List of vehicle media response."""

    media: list[VehicleMediaResponse]
