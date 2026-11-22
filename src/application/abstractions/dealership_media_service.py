from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID

from src.application.dtos.dealership_media_dto import DealershipMediaDTO, DealershipMediaUpdateDTO
from src.domain.entities.user import User


class IDealershipMediaService(ABC):
    """Interface for the dealership photo gallery."""

    @abstractmethod
    async def get_media_by_dealership(self, dealership_id: int) -> list[DealershipMediaDTO]:
        """List the gallery of a dealership."""

    @abstractmethod
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

    @abstractmethod
    async def update_dealership_media(
        self, dealership_id: int, media_id: UUID, update_dto: DealershipMediaUpdateDTO, requesting_user: User
    ) -> DealershipMediaDTO:
        """Change caption or order of a gallery item."""

    @abstractmethod
    async def delete_dealership_media(self, dealership_id: int, media_id: UUID, requesting_user: User) -> None:
        """Remove a gallery item and its S3 object."""

    @abstractmethod
    async def get_dealership_media_file(self, dealership_id: int, media_id: UUID) -> tuple[BytesIO, str]:
        """Return the file body and its content type."""
