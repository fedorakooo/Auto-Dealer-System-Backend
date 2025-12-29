"""Pydantic models for model API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.domain.value_objects.drive_type import DriveType


class ModelCreateRequest(BaseModel):
    """Request body for creating a model."""

    body_type_id: int
    engine_id: int
    transmission_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None

    def to_dto(self) -> ModelCreateDTO:
        return ModelCreateDTO(
            body_type_id=self.body_type_id,
            engine_id=self.engine_id,
            transmission_id=self.transmission_id,
            name=self.name,
            model_code=self.model_code,
            is_in_production=self.is_in_production,
            production_year_start=self.production_year_start,
            production_year_end=self.production_year_end,
            description=self.description,
            drive_type=self.drive_type,
            max_speed_kmh=self.max_speed_kmh,
            acceleration_0_100_sec=self.acceleration_0_100_sec,
            fuel_tank_capacity_l=self.fuel_tank_capacity_l,
            number_of_seats=self.number_of_seats,
            number_of_doors=self.number_of_doors,
            length_mm=self.length_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            curb_weight_kg=self.curb_weight_kg,
            gross_weight_kg=self.gross_weight_kg,
        )


class ModelUpdateRequest(BaseModel):
    """Request body for updating a model."""

    body_type_id: int | None = None
    engine_id: int | None = None
    transmission_id: int | None = None
    name: str | None = None
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int | None = None
    production_year_end: int | None = None
    description: str | None = None
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None

    def to_dto(self) -> ModelUpdateDTO:
        return ModelUpdateDTO(
            body_type_id=self.body_type_id,
            engine_id=self.engine_id,
            transmission_id=self.transmission_id,
            name=self.name,
            model_code=self.model_code,
            is_in_production=self.is_in_production,
            production_year_start=self.production_year_start,
            production_year_end=self.production_year_end,
            description=self.description,
            drive_type=self.drive_type,
            max_speed_kmh=self.max_speed_kmh,
            acceleration_0_100_sec=self.acceleration_0_100_sec,
            fuel_tank_capacity_l=self.fuel_tank_capacity_l,
            number_of_seats=self.number_of_seats,
            number_of_doors=self.number_of_doors,
            length_mm=self.length_mm,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            curb_weight_kg=self.curb_weight_kg,
            gross_weight_kg=self.gross_weight_kg,
        )


class ModelResponse(BaseModel):
    """Single model response model."""

    id: UUID
    body_type_id: int
    engine_id: int
    transmission_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = None
    acceleration_0_100_sec: Decimal | None = None
    fuel_tank_capacity_l: int | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    curb_weight_kg: int | None = None
    gross_weight_kg: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, model: ModelDTO) -> "ModelResponse":
        return cls(
            id=model.id,
            body_type_id=model.body_type_id,
            engine_id=model.engine_id,
            transmission_id=model.transmission_id,
            name=model.name,
            model_code=model.model_code,
            is_in_production=model.is_in_production,
            production_year_start=model.production_year_start,
            production_year_end=model.production_year_end,
            description=model.description,
            drive_type=model.drive_type,
            max_speed_kmh=model.max_speed_kmh,
            acceleration_0_100_sec=model.acceleration_0_100_sec,
            fuel_tank_capacity_l=model.fuel_tank_capacity_l,
            number_of_seats=model.number_of_seats,
            number_of_doors=model.number_of_doors,
            length_mm=model.length_mm,
            width_mm=model.width_mm,
            height_mm=model.height_mm,
            curb_weight_kg=model.curb_weight_kg,
            gross_weight_kg=model.gross_weight_kg,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ModelsResponse(BaseModel):
    """Paginated models response."""

    models: list[ModelResponse]
    total: int
