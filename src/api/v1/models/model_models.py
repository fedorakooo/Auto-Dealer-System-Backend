"""Pydantic models for model API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO


class ModelCreateRequest(BaseModel):
    """Request body for creating a model; engines and gearboxes belong to its trims."""

    body_type_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None

    def to_dto(self) -> ModelCreateDTO:
        """Converts the request to a create DTO."""
        return ModelCreateDTO(**self.model_dump())


class ModelUpdateRequest(BaseModel):
    """Request body for updating a model."""

    body_type_id: int | None = None
    name: str | None = None
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int | None = None
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None

    def to_dto(self) -> ModelUpdateDTO:
        """Converts the request to an update DTO."""
        return ModelUpdateDTO(**self.model_dump())


class ModelResponse(BaseModel):
    """Single model response model."""

    id: UUID
    body_type_id: int
    name: str
    model_code: str | None = None
    is_in_production: bool | None = None
    production_year_start: int = 0
    production_year_end: int | None = None
    description: str | None = None
    number_of_seats: int | None = None
    number_of_doors: int | None = None
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    images: list[str] | None = None  # model appearance photos
    vehicles_in_stock: int = 0
    min_price: Decimal | None = None

    @classmethod
    def from_dto(cls, model: ModelDTO) -> "ModelResponse":
        """Builds the response from a model DTO."""
        return cls(**vars(model))


class ModelsResponse(BaseModel):
    """Paginated models response."""

    models: list[ModelResponse]
    total: int
