"""Pydantic models for trim API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.trim_dto import TrimCreateDTO, TrimDTO, TrimUpdateDTO
from src.domain.value_objects.drive_type import DriveType


class TrimCreateRequest(BaseModel):
    """Request body for creating a trim of the model given in the path."""

    name: str = Field(min_length=1, max_length=100)
    engine_id: int
    transmission_id: int
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = Field(None, gt=0)
    acceleration_0_100_sec: Decimal | None = Field(None, gt=0, max_digits=3, decimal_places=1)
    fuel_tank_capacity_l: int | None = Field(None, gt=0)
    curb_weight_kg: int | None = Field(None, gt=0)
    gross_weight_kg: int | None = Field(None, gt=0)

    def to_dto(self, model_id: UUID) -> TrimCreateDTO:
        """Converts the request to a create DTO for the given model."""
        return TrimCreateDTO(model_id=model_id, **self.model_dump())


class TrimUpdateRequest(BaseModel):
    """Request body for updating a trim."""

    name: str | None = Field(None, min_length=1, max_length=100)
    engine_id: int | None = None
    transmission_id: int | None = None
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = Field(None, gt=0)
    acceleration_0_100_sec: Decimal | None = Field(None, gt=0, max_digits=3, decimal_places=1)
    fuel_tank_capacity_l: int | None = Field(None, gt=0)
    curb_weight_kg: int | None = Field(None, gt=0)
    gross_weight_kg: int | None = Field(None, gt=0)

    def to_dto(self) -> TrimUpdateDTO:
        """Converts the request to an update DTO."""
        return TrimUpdateDTO(**self.model_dump())


class TrimResponse(BaseModel):
    """Single trim response model."""

    id: UUID
    model_id: UUID
    name: str
    engine_id: int
    transmission_id: int
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, trim: TrimDTO) -> "TrimResponse":
        """Builds the response from a trim DTO."""
        return cls(**vars(trim))


class TrimsResponse(BaseModel):
    """Trims of a model."""

    trims: list[TrimResponse]
