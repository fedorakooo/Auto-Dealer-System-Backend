from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)
from src.domain.value_objects.media_type import MediaType


class ModelMediaCreateRequest(BaseModel):
    model_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0

    def to_dto(self) -> ModelMediaCreateDTO:
        return ModelMediaCreateDTO(
            model_id=self.model_id,
            url=self.url,
            media_type=self.media_type,
            description=self.description,
            sort_order=self.sort_order,
        )


class ModelMediaUpdateRequest(BaseModel):
    url: str | None = None
    media_type: MediaType | None = None
    description: str | None = None
    sort_order: int | None = None

    def to_dto(self) -> ModelMediaUpdateDTO:
        return ModelMediaUpdateDTO(
            url=self.url,
            media_type=self.media_type,
            description=self.description,
            sort_order=self.sort_order,
        )


class ModelMediaResponse(BaseModel):
    id: UUID
    model_id: UUID
    url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, media: ModelMediaDTO) -> "ModelMediaResponse":
        return cls(
            id=media.id,
            model_id=media.model_id,
            url=media.url,
            media_type=media.media_type,
            description=media.description,
            sort_order=media.sort_order,
            updated_at=media.updated_at,
        )


class ModelMediaListResponse(BaseModel):
    media: list[ModelMediaResponse]
