from datetime import datetime
from uuid import uuid4

from src.application.dtos.review_dto import ReviewCreateDTO, ReviewDTO, ReviewUpdateDTO
from src.domain.entities.review import Review


class ReviewMapper:
    """Mapper for converting between Review DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(review: Review) -> ReviewDTO:
        return ReviewDTO(
            id=review.id,
            customer_id=review.customer_id,
            model_id=review.model_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    @staticmethod
    def from_create_dto_to_entity(create_dto: ReviewCreateDTO) -> Review:
        now = datetime.utcnow()
        return Review(
            id=uuid4(),
            customer_id=create_dto.customer_id,
            model_id=create_dto.model_id,
            rating=create_dto.rating,
            title=create_dto.title,
            comment=create_dto.comment,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        review: Review,
        update_dto: ReviewUpdateDTO,
    ) -> Review:
        return Review(
            id=review.id,
            customer_id=review.customer_id,
            model_id=review.model_id,
            rating=update_dto.rating if update_dto.rating is not None else review.rating,
            title=update_dto.title if update_dto.title is not None else review.title,
            comment=update_dto.comment if update_dto.comment is not None else review.comment,
            created_at=review.created_at,
            updated_at=datetime.utcnow(),
        )
