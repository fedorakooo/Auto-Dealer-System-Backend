from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.feature_dto import (
    FeatureAttachDTO,
    FeatureCreateDTO,
    FeatureDetachDTO,
    FeatureDTO,
    FeatureUpdateDTO,
)


class IFeatureService(ABC):
    """Interface for feature operations."""

    @abstractmethod
    async def create_feature(self, create_dto: FeatureCreateDTO) -> FeatureDTO:
        """Create a new feature."""
        pass

    @abstractmethod
    async def get_feature(self, feature_id: int) -> FeatureDTO:
        """Get feature by ID."""
        pass

    @abstractmethod
    async def get_all_features(self) -> list[FeatureDTO]:
        """Get all features."""
        pass

    @abstractmethod
    async def get_features_by_model(self, model_id: UUID) -> list[FeatureDTO]:
        """Get features by model ID."""
        pass

    @abstractmethod
    async def get_features_by_custom_order(self, custom_order_id: UUID) -> list[FeatureDTO]:
        """Get features by custom order ID."""
        pass

    @abstractmethod
    async def update_feature(self, feature_id: int, update_dto: FeatureUpdateDTO) -> FeatureDTO:
        """Update feature."""
        pass

    @abstractmethod
    async def delete_feature(self, feature_id: int) -> bool:
        """Delete feature."""
        pass

    @abstractmethod
    async def attach_feature_to_model(self, model_id: UUID, attach_dto: FeatureAttachDTO) -> bool:
        """Attach feature to model."""
        pass

    @abstractmethod
    async def detach_feature_from_model(self, model_id: UUID, detach_dto: FeatureDetachDTO) -> bool:
        """Detach feature from model."""
        pass

    @abstractmethod
    async def attach_feature_to_custom_order(
        self,
        custom_order_id: UUID,
        attach_dto: FeatureAttachDTO,
    ) -> bool:
        """Attach feature to custom order."""
        pass

    @abstractmethod
    async def detach_feature_from_custom_order(
        self,
        custom_order_id: UUID,
        detach_dto: FeatureDetachDTO,
    ) -> bool:
        """Detach feature from custom order."""
        pass
