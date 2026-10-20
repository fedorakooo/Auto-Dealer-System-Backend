from io import BytesIO
from uuid import UUID, uuid4

from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.application.dtos.vehicle_media_dto import (
    VehicleMediaCreateDTO,
    VehicleMediaDTO,
    VehicleMediaUpdateDTO,
)
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.vehicle_media_mapper import VehicleMediaMapper
from src.application.services.media_utils import resolve_content_type, sanitize_filename, validate_image_upload
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.s3.s3_client import IS3Client
from src.domain.value_objects.media_type import MediaType


class VehicleMediaService(IVehicleMediaService):
    def __init__(self, uow: IUnitOfWork, s3_client: IS3Client | None = None):
        self._uow = uow
        self._s3_client = s3_client

    def _require_s3_client(self) -> IS3Client:
        if not self._s3_client:
            raise BusinessError("S3 storage is not configured")
        return self._s3_client

    async def create_vehicle_media(self, create_dto: VehicleMediaCreateDTO) -> VehicleMediaDTO:
        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(create_dto.vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(create_dto.vehicle_id))

            vehicle_media = VehicleMediaMapper.from_create_dto_to_entity(create_dto)
            created_media = await uow.vehicle_media_repository.create(vehicle_media)

        return VehicleMediaMapper.from_entity_to_dto(created_media)

    async def get_vehicle_media(self, media_id: UUID) -> VehicleMediaDTO:
        async with self._uow as uow:
            vehicle_media = await uow.vehicle_media_repository.get_by_id(media_id)
            if not vehicle_media:
                raise NotFoundError("VehicleMedia", str(media_id))
        return VehicleMediaMapper.from_entity_to_dto(vehicle_media)

    async def get_media_by_vehicle(self, vehicle_id: UUID) -> list[VehicleMediaDTO]:
        async with self._uow as uow:
            media_list = await uow.vehicle_media_repository.get_by_vehicle_id(vehicle_id)
        return [VehicleMediaMapper.from_entity_to_dto(media) for media in media_list]

    async def update_vehicle_media(self, media_id: UUID, update_dto: VehicleMediaUpdateDTO) -> VehicleMediaDTO:
        async with self._uow as uow:
            vehicle_media = await uow.vehicle_media_repository.get_by_id(media_id)
            if not vehicle_media:
                raise NotFoundError("VehicleMedia", str(media_id))

            updated_media = VehicleMediaMapper.from_update_dto_to_entity(vehicle_media, update_dto)
            saved_media = await uow.vehicle_media_repository.update(updated_media)

        return VehicleMediaMapper.from_entity_to_dto(saved_media)

    async def delete_vehicle_media(self, media_id: UUID) -> bool:
        async with self._uow as uow:
            vehicle_media = await uow.vehicle_media_repository.get_by_id(media_id)
            if not vehicle_media:
                raise NotFoundError("VehicleMedia", str(media_id))

            if self._s3_client and vehicle_media.url:
                await self._s3_client.delete_file(vehicle_media.url)

            result = await uow.vehicle_media_repository.delete(media_id)
        return result

    async def delete_all_vehicle_media(self, vehicle_id: UUID) -> int:
        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(vehicle_id))

            media_list = await uow.vehicle_media_repository.get_by_vehicle_id(vehicle_id)
            if self._s3_client:
                for media in media_list:
                    if media.url:
                        await self._s3_client.delete_file(media.url)

            count = await uow.vehicle_media_repository.delete_by_vehicle_id(vehicle_id)
        return count

    async def upload_vehicle_media_file(
        self,
        vehicle_id: UUID,
        file_content: bytes,
        filename: str,
        media_type: MediaType,
        description: str | None = None,
        sort_order: int = 0,
    ) -> VehicleMediaDTO:
        """Upload a media file for a vehicle."""
        s3_client = self._require_s3_client()

        if media_type == MediaType.IMAGE:
            validate_image_upload(filename, file_content)

        async with self._uow as uow:
            vehicle = await uow.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(vehicle_id))

            safe_filename = sanitize_filename(filename)
            s3_key = f"vehicles/{vehicle_id}/{uuid4()}_{safe_filename}"
            content_type = resolve_content_type(safe_filename, media_type)
            await s3_client.upload_file(s3_key, file_content, content_type)

            create_dto = VehicleMediaCreateDTO(
                vehicle_id=vehicle_id,
                url=s3_key,
                media_type=media_type,
                description=description,
                sort_order=sort_order,
            )
            vehicle_media = VehicleMediaMapper.from_create_dto_to_entity(create_dto)
            created_media = await uow.vehicle_media_repository.create(vehicle_media)

        return VehicleMediaMapper.from_entity_to_dto(created_media)

    async def get_vehicle_media_file(self, media_id: UUID) -> tuple[BytesIO, str]:
        """Get media file content and content-type from S3."""
        s3_client = self._require_s3_client()

        async with self._uow as uow:
            vehicle_media = await uow.vehicle_media_repository.get_by_id(media_id)
            if not vehicle_media:
                raise NotFoundError("VehicleMedia", str(media_id))

        return await s3_client.get_file(vehicle_media.url)
