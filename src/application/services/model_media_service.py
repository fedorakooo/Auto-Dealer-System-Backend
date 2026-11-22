from io import BytesIO
from uuid import UUID, uuid4

from src.application.abstractions.model_media_service import IModelMediaService
from src.application.dtos.model_media_dto import (
    ModelMediaCreateDTO,
    ModelMediaDTO,
    ModelMediaUpdateDTO,
)
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.model_media_mapper import ModelMediaMapper
from src.application.services.media_utils import resolve_content_type, sanitize_filename, validate_image_upload
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.s3.s3_client import IS3Client
from src.domain.value_objects.media_type import MediaType

class ModelMediaService(IModelMediaService):
    def __init__(self, uow: IUnitOfWork, s3_client: IS3Client | None = None):
        self._uow = uow
        self._s3_client = s3_client

    def _require_s3_client(self) -> IS3Client:
        if not self._s3_client:
            raise BusinessError("S3 storage is not configured")
        return self._s3_client

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

            if self._s3_client and model_media.url:
                await self._s3_client.delete_file(model_media.url)

            result = await uow.model_media_repository.delete(media_id)
        return result

    async def delete_all_model_media(self, model_id: UUID) -> int:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            media_list = await uow.model_media_repository.get_by_model_id(model_id)
            if self._s3_client:
                for media in media_list:
                    if media.url:
                        await self._s3_client.delete_file(media.url)

            count = await uow.model_media_repository.delete_by_model_id(model_id)
        return count

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
        s3_client = self._require_s3_client()

        if media_type == MediaType.IMAGE:
            validate_image_upload(filename, file_content)

        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            safe_filename = sanitize_filename(filename)
            s3_key = f"models/{model_id}/{uuid4()}_{safe_filename}"
            content_type = resolve_content_type(safe_filename, media_type)
            await s3_client.upload_file(s3_key, file_content, content_type)

            create_dto = ModelMediaCreateDTO(
                model_id=model_id,
                url=s3_key,
                media_type=media_type,
                description=description,
                sort_order=sort_order,
            )
            model_media = ModelMediaMapper.from_create_dto_to_entity(create_dto)
            created_media = await uow.model_media_repository.create(model_media)

        return ModelMediaMapper.from_entity_to_dto(created_media)

    async def get_model_media_file(self, media_id: UUID) -> tuple[BytesIO, str]:
        """Get media file content and content-type from S3."""
        s3_client = self._require_s3_client()

        async with self._uow as uow:
            model_media = await uow.model_media_repository.get_by_id(media_id)
            if not model_media:
                raise NotFoundError("ModelMedia", str(media_id))

        return await s3_client.get_file(model_media.url)
