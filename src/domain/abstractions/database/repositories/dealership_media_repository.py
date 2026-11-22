from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.dealership_media import DealershipMedia


class IDealershipMediaRepository(ABC):
    """Interface for dealership media repository operations."""

    @abstractmethod
    async def get_by_id(self, media_id: UUID) -> DealershipMedia | None:
        """Returns one dealership media by ID or None."""

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[DealershipMedia]:
        """Returns the gallery of a dealership ordered by sort_order."""

    @abstractmethod
    async def get_cover_ids(self, dealership_ids: list[int]) -> dict[int, UUID]:
        """Returns the first image of each dealership gallery, keyed by dealership ID."""

    @abstractmethod
    async def create(self, media: DealershipMedia) -> DealershipMedia:
        """Creates a dealership media record."""

    @abstractmethod
    async def update(self, media: DealershipMedia) -> DealershipMedia:
        """Updates a dealership media record."""

    @abstractmethod
    async def delete(self, media_id: UUID) -> bool:
        """Deletes a dealership media record by its ID."""
