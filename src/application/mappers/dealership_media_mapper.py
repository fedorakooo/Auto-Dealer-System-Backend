from src.application.dtos.dealership_media_dto import DealershipMediaDTO
from src.domain.entities.dealership_media import DealershipMedia


class DealershipMediaMapper:
    """Mapper for dealership gallery items."""

    @staticmethod
    def to_dto(media: DealershipMedia) -> DealershipMediaDTO:
        """Maps a dealership media entity to a DTO."""
        return DealershipMediaDTO(
            id=media.id,
            dealership_id=media.dealership_id,
            url=media.url,
            media_type=media.media_type,
            description=media.description,
            sort_order=media.sort_order,
            updated_at=media.updated_at,
        )
