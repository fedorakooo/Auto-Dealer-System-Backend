from src.application.dtos.dealership_review_dto import (
    DealershipRatingSummaryDTO,
    DealershipReviewCommentDTO,
    DealershipReviewDTO,
)
from src.domain.entities.dealership_review import (
    DealershipRatingSummary,
    DealershipReview,
    DealershipReviewComment,
)


class DealershipReviewMapper:
    """Mapper for dealership reviews, their comments and the rating summary."""

    @staticmethod
    def comment_to_dto(comment: DealershipReviewComment) -> DealershipReviewCommentDTO:
        """Maps a review comment entity to a DTO."""
        return DealershipReviewCommentDTO(
            id=comment.id,
            review_id=comment.review_id,
            author_user_id=comment.author_user_id,
            body=comment.body,
            is_official=comment.is_official,
            author_name=comment.author_name,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    @staticmethod
    def review_to_dto(review: DealershipReview) -> DealershipReviewDTO:
        """Maps a review entity to a DTO."""
        return DealershipReviewDTO(
            id=review.id,
            dealership_id=review.dealership_id,
            customer_id=review.customer_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            is_hidden=review.is_hidden,
            author_name=review.author_name,
            is_verified_customer=review.is_verified_customer,
            comments=[DealershipReviewMapper.comment_to_dto(c) for c in review.comments],
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    @staticmethod
    def summary_to_dto(summary: DealershipRatingSummary | None) -> DealershipRatingSummaryDTO:
        """Maps a rating summary to a DTO."""
        if summary is None:
            return DealershipRatingSummaryDTO()
        return DealershipRatingSummaryDTO(
            reviews_count=summary.reviews_count,
            average_rating=summary.average_rating,
            distribution=dict(summary.distribution),
        )
