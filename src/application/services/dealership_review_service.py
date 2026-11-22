from uuid import UUID, uuid4

from src.application.abstractions.dealership_review_service import IDealershipReviewService
from src.application.dtos.dealership_review_dto import (
    DealershipReviewCommentDTO,
    DealershipReviewCreateDTO,
    DealershipReviewDTO,
    DealershipReviewPageDTO,
    DealershipReviewUpdateDTO,
)
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.dealership_review_mapper import DealershipReviewMapper
from src.application.services.dealership_access import can_manage_dealership, ensure_can_manage_dealership
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.entities.dealership_review import DealershipReview, DealershipReviewComment
from src.domain.entities.user import User
from src.domain.exceptions.auth_errors import ForbiddenError
from src.domain.value_objects.user_role import UserRole


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


class DealershipReviewService(IDealershipReviewService):
    """Service for dealership reviews, moderation and comments."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    @staticmethod
    async def _require_dealership(uow: IUnitOfWork, dealership_id: int) -> None:
        if not await uow.dealership_repository.get_by_id(dealership_id):
            raise NotFoundError("Dealership", str(dealership_id))

    @staticmethod
    async def _require_review(uow: IUnitOfWork, dealership_id: int, review_id: UUID) -> DealershipReview:
        review = await uow.dealership_review_repository.get_by_id(review_id)
        if not review or review.dealership_id != dealership_id:
            raise NotFoundError("Dealership review", str(review_id))
        return review

    @staticmethod
    async def _customer_id_of(uow: IUnitOfWork, user: User | None) -> UUID | None:
        if user is None or user.role != UserRole.CUSTOMER:
            return None
        customer = await uow.customer_repository.get_by_user_id(user.id)
        return customer.id if customer else None

    async def list_reviews(
        self, dealership_id: int, viewer: User | None, include_hidden: bool, page: int, limit: int
    ) -> DealershipReviewPageDTO:
        """Page of reviews with comments and the rating summary; hidden ones only for the dealership's staff."""
        async with self._uow as uow:
            await self._require_dealership(uow, dealership_id)
            if include_hidden:
                await ensure_can_manage_dealership(uow, viewer, dealership_id)

            reviews, total = await uow.dealership_review_repository.get_page(
                dealership_id=dealership_id,
                include_hidden=include_hidden,
                viewer_customer_id=await self._customer_id_of(uow, viewer),
                offset=(page - 1) * limit,
                limit=limit,
            )
            summaries = await uow.dealership_review_repository.get_rating_summaries([dealership_id])

        return DealershipReviewPageDTO(
            reviews=[DealershipReviewMapper.review_to_dto(r) for r in reviews],
            total=total,
            summary=DealershipReviewMapper.summary_to_dto(summaries.get(dealership_id)),
        )

    async def create_review(
        self, dealership_id: int, create_dto: DealershipReviewCreateDTO, requesting_user: User
    ) -> DealershipReviewDTO:
        """Create the customer's single review of a dealership."""
        if not 1 <= create_dto.rating <= 5:
            raise ValidationError("Rating must be between 1 and 5")

        async with self._uow as uow:
            await self._require_dealership(uow, dealership_id)
            customer_id = await self._customer_id_of(uow, requesting_user)
            if customer_id is None:
                raise ForbiddenError()

            existing = await uow.dealership_review_repository.get_by_dealership_and_customer(dealership_id, customer_id)
            if existing:
                raise BusinessError("You have already reviewed this dealership")

            review = DealershipReview(
                id=uuid4(),
                dealership_id=dealership_id,
                customer_id=customer_id,
                rating=create_dto.rating,
                title=_clean(create_dto.title),
                comment=_clean(create_dto.comment),
            )
            created = await uow.dealership_review_repository.create(review)

        return DealershipReviewMapper.review_to_dto(created)

    async def update_review(
        self, dealership_id: int, review_id: UUID, update_dto: DealershipReviewUpdateDTO, requesting_user: User
    ) -> DealershipReviewDTO:
        """Edit an own review."""
        if update_dto.rating is not None and not 1 <= update_dto.rating <= 5:
            raise ValidationError("Rating must be between 1 and 5")

        async with self._uow as uow:
            review = await self._require_review(uow, dealership_id, review_id)
            if await self._customer_id_of(uow, requesting_user) != review.customer_id:
                raise ForbiddenError()

            if update_dto.rating is not None:
                review.rating = update_dto.rating
            if update_dto.title is not None:
                review.title = _clean(update_dto.title)
            if update_dto.comment is not None:
                review.comment = _clean(update_dto.comment)
            saved = await uow.dealership_review_repository.update(review)

        return DealershipReviewMapper.review_to_dto(saved)

    async def delete_review(self, dealership_id: int, review_id: UUID, requesting_user: User) -> None:
        """Delete a review; allowed to its author and to an admin."""
        async with self._uow as uow:
            review = await self._require_review(uow, dealership_id, review_id)
            is_author = await self._customer_id_of(uow, requesting_user) == review.customer_id
            if not is_author and requesting_user.role != UserRole.ADMIN:
                raise ForbiddenError()
            await uow.dealership_review_repository.delete(review_id)

    async def set_review_visibility(
        self, dealership_id: int, review_id: UUID, is_hidden: bool, requesting_user: User
    ) -> DealershipReviewDTO:
        """Hide or show a review; allowed to the dealership's staff."""
        async with self._uow as uow:
            review = await self._require_review(uow, dealership_id, review_id)
            await ensure_can_manage_dealership(uow, requesting_user, dealership_id)
            review.is_hidden = is_hidden
            saved = await uow.dealership_review_repository.update(review)

        return DealershipReviewMapper.review_to_dto(saved)

    async def add_comment(
        self, dealership_id: int, review_id: UUID, body: str, requesting_user: User
    ) -> DealershipReviewCommentDTO:
        """Comment under a review: by its author, or an official reply by the dealership's staff."""
        text = _clean(body)
        if not text:
            raise ValidationError("Comment must not be empty")

        async with self._uow as uow:
            review = await self._require_review(uow, dealership_id, review_id)
            if requesting_user.role == UserRole.CUSTOMER:
                if await self._customer_id_of(uow, requesting_user) != review.customer_id:
                    raise ForbiddenError()
                is_official = False
            else:
                await ensure_can_manage_dealership(uow, requesting_user, dealership_id)
                is_official = True

            comment = DealershipReviewComment(
                id=uuid4(),
                review_id=review_id,
                author_user_id=requesting_user.id,
                body=text,
                is_official=is_official,
            )
            created = await uow.dealership_review_repository.create_comment(comment)

        return DealershipReviewMapper.comment_to_dto(created)

    async def delete_comment(
        self, dealership_id: int, review_id: UUID, comment_id: UUID, requesting_user: User
    ) -> None:
        """Delete a comment; allowed to its author and to the dealership's staff."""
        async with self._uow as uow:
            await self._require_review(uow, dealership_id, review_id)
            comment = await uow.dealership_review_repository.get_comment(comment_id)
            if not comment or comment.review_id != review_id:
                raise NotFoundError("Review comment", str(comment_id))

            is_author = comment.author_user_id == requesting_user.id
            if not is_author and not await can_manage_dealership(uow, requesting_user, dealership_id):
                raise ForbiddenError()
            await uow.dealership_review_repository.delete_comment(comment_id)
