from src.application.dtos.feature_dto import (
    FeatureCreateDTO,
    FeatureDTO,
    FeatureUpdateDTO,
)
from src.domain.entities.feature import Feature


class FeatureMapper:
    """Mapper for converting between Feature DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(feature: Feature) -> FeatureDTO:
        return FeatureDTO(
            id=feature.id,
            name=feature.name,
            description=feature.description,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: FeatureCreateDTO, feature_id: int) -> Feature:
        return Feature(
            id=feature_id,
            name=create_dto.name,
            description=create_dto.description,
        )

    @staticmethod
    def from_update_dto_to_entity(
        feature: Feature,
        update_dto: FeatureUpdateDTO,
    ) -> Feature:
        return Feature(
            id=feature.id,
            name=update_dto.name if update_dto.name is not None else feature.name,
            description=update_dto.description if update_dto.description is not None else feature.description,
        )
