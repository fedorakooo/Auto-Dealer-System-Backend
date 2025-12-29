from io import BytesIO
from uuid import UUID

from src.application.abstractions.model_media_service import IModelMediaService
from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)
from src.application.exceptions.errors import NotFoundError
from src.application.mappers.model_media_mapper import ModelMediaMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.s3.s3_client import IS3Client
from src.domain.value_objects.media_type import MediaType


class ModelMediaService(IModelMediaService):
    def __init__(self, uow: IUnitOfWork, s3_client: IS3Client | None = None):
        self._uow = uow
        self._s3_client = s3_client

    async def create_model_media(self, create_dto: ModelMediaCreateDTO) -> ModelMediaDTO:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(create_dto.model_id)
            if not model:
                raise NotFoundError("Model", str(create_dto.model_id))

            model_media = ModelMediaMapper.from_create_dto_to_entity(create_dto)
            created_media = await uow.model_media_repository.create(model_media)

        return ModelMediaMapper.from_entity_to_dto(created_media)

    async def get_model_media(self, media_id: UUID) -> ModelMediaDTO:
        async with self._uow as uow:
            model_media = await uow.model_media_repository.get_by_id(media_id)
            if not model_media:
                raise NotFoundError("ModelMedia", str(media_id))
        return ModelMediaMapper.from_entity_to_dto(model_media)

    async def get_media_by_model(self, model_id: UUID) -> list[ModelMediaDTO]:
        async with self._uow as uow:
            media_list = await uow.model_media_repository.get_by_model_id(model_id)
        return [ModelMediaMapper.from_entity_to_dto(media) for media in media_list]

    async def update_model_media(self, media_id: UUID, update_dto: ModelMediaUpdateDTO) -> ModelMediaDTO:
        async with self._uow as uow:
            model_media = await uow.model_media_repository.get_by_id(media_id)
            if not model_media:
                raise NotFoundError("ModelMedia", str(media_id))

            updated_media = ModelMediaMapper.from_update_dto_to_entity(model_media, update_dto)
            saved_media = await uow.model_media_repository.update(updated_media)

        return ModelMediaMapper.from_entity_to_dto(saved_media)

    async def delete_model_media(self, media_id: UUID) -> bool:
        async with self._uow as uow:
            model_media = await uow.model_media_repository.get_by_id(media_id)
            if not model_media:
                raise NotFoundError("ModelMedia", str(media_id))

            # Delete file from S3 if client is available
            if self._s3_client and model_media.url:
                # Extract key from URL
                key = model_media.url.split("/")[-1] if "/" in model_media.url else model_media.url
                await self._s3_client.delete_file(key)

            result = await uow.model_media_repository.delete(media_id)
        return result

    async def delete_all_model_media(self, model_id: UUID) -> int:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            # Get all media to delete from S3
            media_list = await uow.model_media_repository.get_by_model_id(model_id)
            if self._s3_client:
                for media in media_list:
                    if media.url:
                        key = media.url.split("/")[-1] if "/" in media.url else media.url
                        await self._s3_client.delete_file(key)

            count = await uow.model_media_repository.delete_by_model_id(model_id)
        return count

    async def upload_model_media_file(
        self, model_id: UUID, file_content: bytes, filename: str, media_type: MediaType, description: str | None = None
    ) -> ModelMediaDTO:
        """Upload a media file for a model."""
        if not self._s3_client:
            raise ValueError("S3 client is not configured")

        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            # Generate S3 key
            file_extension = filename.split(".")[-1] if "." in filename else ""
            s3_key = f"models/{model_id}/{filename}"

            # Upload to S3
            content_type = f"image/{file_extension}" if media_type == MediaType.IMAGE else f"video/{file_extension}"
            await self._s3_client.upload_file(s3_key, file_content, content_type)

            # Create media record
            create_dto = ModelMediaCreateDTO(
                model_id=model_id,
                url=s3_key,
                media_type=media_type,
                description=description,
            )
            model_media = ModelMediaMapper.from_create_dto_to_entity(create_dto)
            created_media = await uow.model_media_repository.create(model_media)

        return ModelMediaMapper.from_entity_to_dto(created_media)

    async def get_model_media_file(self, media_id: UUID) -> BytesIO:
        """Get media file content from S3."""
        if not self._s3_client:
            raise ValueError("S3 client is not configured")

        async with self._uow as uow:
            model_media = await uow.model_media_repository.get_by_id(media_id)
            if not model_media:
                raise NotFoundError("ModelMedia", str(media_id))

        # Get file from S3
        return await self._s3_client.get_file(model_media.url)
