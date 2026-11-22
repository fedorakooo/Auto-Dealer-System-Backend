from datetime import datetime
from uuid import uuid4

from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.domain.entities.model import Model


class ModelMapper:
    """Mapper for converting between Model DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(model: Model) -> ModelDTO:
        """Maps a model entity to a DTO."""
        return ModelDTO(
            id=model.id,
            body_type_id=model.body_type_id,
            name=model.name,
            model_code=model.model_code,
            is_in_production=model.is_in_production,
            production_year_start=model.production_year_start,
            production_year_end=model.production_year_end,
            description=model.description,
            number_of_seats=model.number_of_seats,
            number_of_doors=model.number_of_doors,
            length_mm=model.length_mm,
            width_mm=model.width_mm,
            height_mm=model.height_mm,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: ModelCreateDTO) -> Model:
        """Builds a new model entity from a create DTO."""
        return Model(
            id=uuid4(),
            body_type_id=create_dto.body_type_id,
            name=create_dto.name,
            model_code=create_dto.model_code,
            is_in_production=create_dto.is_in_production,
            production_year_start=create_dto.production_year_start,
            production_year_end=create_dto.production_year_end,
            description=create_dto.description,
            number_of_seats=create_dto.number_of_seats,
            number_of_doors=create_dto.number_of_doors,
            length_mm=create_dto.length_mm,
            width_mm=create_dto.width_mm,
            height_mm=create_dto.height_mm,
            created_at=datetime.utcnow(),
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(model: Model, update_dto: ModelUpdateDTO) -> Model:
        """Applies an update DTO to a model entity."""
        changes = {name: value for name, value in vars(update_dto).items() if value is not None}
        return Model(**{**vars(model), **changes, "updated_at": datetime.utcnow()})
