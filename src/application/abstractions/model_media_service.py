from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID

from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)
from src.domain.value_objects.media_type import MediaType


class IModelMediaService(ABC):
    """Interface for model media operations."""

    @abstractmethod
    async def create_model_media(self, create_dto: ModelMediaCreateDTO) -> ModelMediaDTO:
        """Create a new model media."""
        pass

    @abstractmethod
    async def get_model_media(self, media_id: UUID) -> ModelMediaDTO:
        """Get model media by ID."""
        pass

    @abstractmethod
    async def get_media_by_model(self, model_id: UUID) -> list[ModelMediaDTO]:
        """Get model media by model ID."""
        pass

    @abstractmethod
    async def update_model_media(
        self,
        media_id: UUID,
        update_dto: ModelMediaUpdateDTO,
    ) -> ModelMediaDTO:
        """Update model media."""
        pass

    @abstractmethod
    async def delete_model_media(self, media_id: UUID) -> bool:
        """Delete model media."""
        pass

    @abstractmethod
    async def delete_all_model_media(self, model_id: UUID) -> int:
        """Delete all media for a model."""
        pass

    @abstractmethod
    async def upload_model_media_file(
        self,
        model_id: UUID,
        file_content: bytes,
        filename: str,
        media_type: MediaType,
        description: str | None = None,
        sort_order: int = 0,
    ) -> ModelMediaDTO:
        """Upload a media file for a model."""
        pass

    @abstractmethod
    async def get_model_media_file(self, media_id: UUID) -> tuple[BytesIO, str]:
        """Get media file content and content-type from S3."""
        pass
