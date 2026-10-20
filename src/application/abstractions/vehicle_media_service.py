from abc import ABC, abstractmethod
from io import BytesIO
from uuid import UUID

from src.application.dtos.vehicle_media_dto import (
    VehicleMediaCreateDTO,
    VehicleMediaDTO,
    VehicleMediaUpdateDTO,
)
from src.domain.value_objects.media_type import MediaType


class IVehicleMediaService(ABC):
    """Interface for vehicle media operations."""

    @abstractmethod
    async def create_vehicle_media(self, create_dto: VehicleMediaCreateDTO) -> VehicleMediaDTO:
        """Create a new vehicle media."""
        pass

    @abstractmethod
    async def get_vehicle_media(self, media_id: UUID) -> VehicleMediaDTO:
        """Get vehicle media by ID."""
        pass

    @abstractmethod
    async def get_media_by_vehicle(self, vehicle_id: UUID) -> list[VehicleMediaDTO]:
        """Get vehicle media by vehicle ID."""
        pass

    @abstractmethod
    async def update_vehicle_media(
        self,
        media_id: UUID,
        update_dto: VehicleMediaUpdateDTO,
    ) -> VehicleMediaDTO:
        """Update vehicle media."""
        pass

    @abstractmethod
    async def delete_vehicle_media(self, media_id: UUID) -> bool:
        """Delete vehicle media."""
        pass

    @abstractmethod
    async def delete_all_vehicle_media(self, vehicle_id: UUID) -> int:
        """Delete all media for a vehicle."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_vehicle_media_file(self, media_id: UUID) -> tuple[BytesIO, str]:
        """Get media file content and content-type from S3."""
        pass
