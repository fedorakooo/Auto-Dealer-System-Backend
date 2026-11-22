"""Pydantic models for the dealership photo gallery API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.dealership_media_dto import DealershipMediaDTO, DealershipMediaUpdateDTO
from src.domain.value_objects.media_type import MediaType


class DealershipMediaUpdateRequest(BaseModel):
    """Request body for updating dealership photo metadata."""

    description: str | None = Field(None, max_length=500, description="Blank text clears the caption")
    sort_order: int | None = None

    def to_dto(self) -> DealershipMediaUpdateDTO:
        """Converts the request to an update DTO."""
        return DealershipMediaUpdateDTO(description=self.description, sort_order=self.sort_order)


class DealershipMediaResponse(BaseModel):
    """Dealership photo returned by the API."""

    id: UUID
    dealership_id: int
    file_url: str
    media_type: MediaType
    description: str | None = None
    sort_order: int = 0
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, media: DealershipMediaDTO) -> "DealershipMediaResponse":
        """Builds the response from a dealership media DTO."""
        return cls(
            id=media.id,
            dealership_id=media.dealership_id,
            file_url=f"/api/v1/dealerships/{media.dealership_id}/media/{media.id}/file",
            media_type=media.media_type,
            description=media.description,
            sort_order=media.sort_order,
            updated_at=media.updated_at,
        )


class DealershipMediaListResponse(BaseModel):
    """List of dealership photos."""

    media: list[DealershipMediaResponse]
