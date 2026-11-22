from datetime import datetime
from uuid import uuid4

from src.application.dtos.trim_dto import TrimCreateDTO, TrimDTO, TrimUpdateDTO
from src.domain.entities.trim import Trim


class TrimMapper:
    """Mapper for converting between Trim DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(trim: Trim) -> TrimDTO:
        """Maps a trim entity to a DTO."""
        return TrimDTO(**vars(trim))

    @staticmethod
    def from_create_dto_to_entity(create_dto: TrimCreateDTO) -> Trim:
        """Builds a new trim entity from a create DTO."""
        return Trim(id=uuid4(), **vars(create_dto), created_at=datetime.utcnow(), updated_at=None)

    @staticmethod
    def from_update_dto_to_entity(trim: Trim, update_dto: TrimUpdateDTO) -> Trim:
        """Applies an update DTO to a trim entity."""
        changes = {name: value for name, value in vars(update_dto).items() if value is not None}
        return Trim(**{**vars(trim), **changes, "updated_at": datetime.utcnow()})
