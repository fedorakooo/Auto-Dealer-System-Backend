from datetime import datetime
from uuid import uuid4

from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)
from src.domain.entities.model_media import ModelMedia


class ModelMediaMapper:
    """Mapper for converting between ModelMedia DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(model_media: ModelMedia) -> ModelMediaDTO:
        return ModelMediaDTO(
            id=model_media.id,
            model_id=model_media.model_id,
            url=model_media.url,
            media_type=model_media.media_type,
            description=model_media.description,
            sort_order=model_media.sort_order,
            updated_at=model_media.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: ModelMediaCreateDTO) -> ModelMedia:
        return ModelMedia(
            id=uuid4(),
            model_id=create_dto.model_id,
            url=create_dto.url,
            media_type=create_dto.media_type,
            description=create_dto.description,
            sort_order=create_dto.sort_order,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        model_media: ModelMedia,
        update_dto: ModelMediaUpdateDTO,
    ) -> ModelMedia:
        return ModelMedia(
            id=model_media.id,
            model_id=model_media.model_id,
            url=update_dto.url if update_dto.url is not None else model_media.url,
            media_type=update_dto.media_type if update_dto.media_type is not None else model_media.media_type,
            description=update_dto.description if update_dto.description is not None else model_media.description,
            sort_order=update_dto.sort_order if update_dto.sort_order is not None else model_media.sort_order,
            updated_at=datetime.utcnow(),
        )
