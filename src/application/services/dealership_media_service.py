from io import BytesIO
from uuid import UUID, uuid4

from src.application.abstractions.dealership_media_service import IDealershipMediaService
from src.application.dtos.dealership_media_dto import DealershipMediaDTO, DealershipMediaUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.dealership_media_mapper import DealershipMediaMapper
from src.application.services.dealership_access import ensure_can_manage_dealership
from src.application.services.media_utils import resolve_content_type, sanitize_filename, validate_image_upload
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.abstractions.s3.s3_client import IS3Client
from src.domain.entities.dealership_media import DealershipMedia
from src.domain.entities.user import User
from src.domain.exceptions.storage_errors import StorageObjectNotFoundError
from src.domain.value_objects.media_type import MediaType


class DealershipMediaService(IDealershipMediaService):
    """Service for dealership photo galleries."""

    def __init__(self, uow: IUnitOfWork, s3_client: IS3Client | None = None) -> None:
        self._uow = uow
        self._s3_client = s3_client

    def _require_s3_client(self) -> IS3Client:
        if not self._s3_client:
            raise BusinessError("S3 storage is not configured")
        return self._s3_client

    @staticmethod
    async def _require_dealership(uow: IUnitOfWork, dealership_id: int) -> None:
        if not await uow.dealership_repository.get_by_id(dealership_id):
            raise NotFoundError("Dealership", str(dealership_id))

    @staticmethod
    async def _require_media(uow: IUnitOfWork, dealership_id: int, media_id: UUID) -> DealershipMedia:
        media = await uow.dealership_media_repository.get_by_id(media_id)
        if not media or media.dealership_id != dealership_id:
            raise NotFoundError("Dealership media", str(media_id))
        return media

    async def get_media_by_dealership(self, dealership_id: int) -> list[DealershipMediaDTO]:
        """List the gallery of a dealership."""
        async with self._uow as uow:
            await self._require_dealership(uow, dealership_id)
            media_list = await uow.dealership_media_repository.get_by_dealership_id(dealership_id)
        return [DealershipMediaMapper.to_dto(m) for m in media_list]

    async def upload_dealership_media_file(
        self,
        dealership_id: int,
        file_content: bytes,
        filename: str,
        requesting_user: User,
        description: str | None = None,
        sort_order: int = 0,
    ) -> DealershipMediaDTO:
        """Store an image in S3 and add it to the gallery."""
        s3_client = self._require_s3_client()
        validate_image_upload(filename, file_content)

        async with self._uow as uow:
            await self._require_dealership(uow, dealership_id)
            await ensure_can_manage_dealership(uow, requesting_user, dealership_id)

            safe_filename = sanitize_filename(filename)
            s3_key = f"dealerships/{dealership_id}/{uuid4()}_{safe_filename}"
            await s3_client.upload_file(s3_key, file_content, resolve_content_type(safe_filename, MediaType.IMAGE))

            media = DealershipMedia(
                id=uuid4(),
                dealership_id=dealership_id,
                url=s3_key,
                media_type=MediaType.IMAGE,
                description=(description or "").strip() or None,
                sort_order=sort_order,
            )
            created = await uow.dealership_media_repository.create(media)

        return DealershipMediaMapper.to_dto(created)

    async def update_dealership_media(
        self, dealership_id: int, media_id: UUID, update_dto: DealershipMediaUpdateDTO, requesting_user: User
    ) -> DealershipMediaDTO:
        """Change caption or order of a gallery item."""
        async with self._uow as uow:
            media = await self._require_media(uow, dealership_id, media_id)
            await ensure_can_manage_dealership(uow, requesting_user, dealership_id)

            if update_dto.description is not None:
                media.description = update_dto.description.strip() or None
            if update_dto.sort_order is not None:
                media.sort_order = update_dto.sort_order
            saved = await uow.dealership_media_repository.update(media)

        return DealershipMediaMapper.to_dto(saved)

    async def delete_dealership_media(self, dealership_id: int, media_id: UUID, requesting_user: User) -> None:
        """Remove a gallery item and its S3 object."""
        async with self._uow as uow:
            media = await self._require_media(uow, dealership_id, media_id)
            await ensure_can_manage_dealership(uow, requesting_user, dealership_id)

            await uow.dealership_media_repository.delete(media_id)
            if self._s3_client and media.url:
                await self._s3_client.delete_file(media.url)

    async def get_dealership_media_file(self, dealership_id: int, media_id: UUID) -> tuple[BytesIO, str]:
        """Return the file body and its content type."""
        s3_client = self._require_s3_client()

        async with self._uow as uow:
            media = await self._require_media(uow, dealership_id, media_id)

        try:
            return await s3_client.get_file(media.url)
        except StorageObjectNotFoundError as exc:
            raise NotFoundError("Dealership media file", str(media_id)) from exc
