"""Pydantic models for feature API."""

from pydantic import BaseModel

from src.application.dtos.feature_dto import (
    FeatureAttachDTO,
    FeatureCreateDTO,
    FeatureDetachDTO,
    FeatureDTO,
    FeatureUpdateDTO,
)


class FeatureCreateRequest(BaseModel):
    """Request body for creating a feature."""

    name: str
    description: str | None = None

    def to_dto(self) -> FeatureCreateDTO:
        return FeatureCreateDTO(
            name=self.name,
            description=self.description,
        )


class FeatureUpdateRequest(BaseModel):
    """Request body for updating a feature."""

    name: str | None = None
    description: str | None = None

    def to_dto(self) -> FeatureUpdateDTO:
        return FeatureUpdateDTO(
            name=self.name,
            description=self.description,
        )


class FeatureResponse(BaseModel):
    """Single feature response model."""

    id: int
    name: str
    description: str | None = None

    @classmethod
    def from_dto(cls, feature: FeatureDTO) -> "FeatureResponse":
        return cls(
            id=feature.id,
            name=feature.name,
            description=feature.description,
        )


class FeaturesResponse(BaseModel):
    """List of features response."""

    features: list[FeatureResponse]


class FeatureAttachRequest(BaseModel):
    """Request body for attaching a feature."""

    feature_id: int

    def to_dto(self) -> FeatureAttachDTO:
        return FeatureAttachDTO(feature_id=self.feature_id)


class FeatureDetachRequest(BaseModel):
    """Request body for detaching a feature."""

    feature_id: int

    def to_dto(self) -> FeatureDetachDTO:
        return FeatureDetachDTO(feature_id=self.feature_id)
