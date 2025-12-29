from datetime import datetime
from uuid import uuid4

from src.application.dtos.vehicle_media_dto import (
    VehicleMediaCreateDTO,
    VehicleMediaDTO,
    VehicleMediaUpdateDTO,
)
from src.domain.entities.vehicle_media import VehicleMedia


class VehicleMediaMapper:
    """Mapper for converting between VehicleMedia DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(vehicle_media: VehicleMedia) -> VehicleMediaDTO:
        return VehicleMediaDTO(
            id=vehicle_media.id,
            vehicle_id=vehicle_media.vehicle_id,
            url=vehicle_media.url,
            media_type=vehicle_media.media_type,
            description=vehicle_media.description,
            sort_order=vehicle_media.sort_order,
            updated_at=vehicle_media.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: VehicleMediaCreateDTO) -> VehicleMedia:
        return VehicleMedia(
            id=uuid4(),
            vehicle_id=create_dto.vehicle_id,
            url=create_dto.url,
            media_type=create_dto.media_type,
            description=create_dto.description,
            sort_order=create_dto.sort_order,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        vehicle_media: VehicleMedia,
        update_dto: VehicleMediaUpdateDTO,
    ) -> VehicleMedia:
        return VehicleMedia(
            id=vehicle_media.id,
            vehicle_id=vehicle_media.vehicle_id,
            url=update_dto.url if update_dto.url is not None else vehicle_media.url,
            media_type=update_dto.media_type if update_dto.media_type is not None else vehicle_media.media_type,
            description=update_dto.description if update_dto.description is not None else vehicle_media.description,
            sort_order=update_dto.sort_order if update_dto.sort_order is not None else vehicle_media.sort_order,
            updated_at=datetime.utcnow(),
        )
