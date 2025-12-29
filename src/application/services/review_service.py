from uuid import UUID

from src.application.abstractions.review_service import IReviewService
from src.application.dtos.review_dto import ReviewCreateDTO, ReviewDTO, ReviewUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.review_mapper import ReviewMapper
from src.domain.abstractions.database.uow import IUnitOfWork


class ReviewService(IReviewService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_review(self, create_dto: ReviewCreateDTO) -> ReviewDTO:
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(create_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(create_dto.customer_id))

            model = await uow.model_repository.get_by_id(create_dto.model_id)
            if not model:
                raise NotFoundError("Model", str(create_dto.model_id))

            if not (1 <= create_dto.rating <= 5):
                raise ValidationError("Rating must be between 1 and 5")

            existing_reviews = await uow.review_repository.get_by_customer_id(create_dto.customer_id)
            for review in existing_reviews:
                if review.model_id == create_dto.model_id:
                    raise BusinessError("You have already reviewed this model")

            review = ReviewMapper.from_create_dto_to_entity(create_dto)
            created_review = await uow.review_repository.create(review)

        return ReviewMapper.from_entity_to_dto(created_review)

    async def get_review(self, review_id: UUID) -> ReviewDTO:
        async with self._uow as uow:
            review = await uow.review_repository.get_by_id(review_id)
            if not review:
                raise NotFoundError("Review", str(review_id))
        return ReviewMapper.from_entity_to_dto(review)

    async def get_reviews_by_model(self, model_id: UUID) -> list[ReviewDTO]:
        async with self._uow as uow:
            reviews = await uow.review_repository.get_by_model_id(model_id)
        return [ReviewMapper.from_entity_to_dto(review) for review in reviews]

    async def get_reviews_by_customer(self, customer_id: UUID) -> list[ReviewDTO]:
        async with self._uow as uow:
            reviews = await uow.review_repository.get_by_customer_id(customer_id)
        return [ReviewMapper.from_entity_to_dto(review) for review in reviews]

    async def update_review(
        self, review_id: UUID, update_dto: ReviewUpdateDTO, current_user_id: UUID | None = None
    ) -> ReviewDTO:
        async with self._uow as uow:
            review = await uow.review_repository.get_by_id(review_id)
            if not review:
                raise NotFoundError("Review", str(review_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                customer = await uow.customer_repository.get_by_user_id(current_user_id)
                if not customer or customer.id != review.customer_id:
                    raise PermissionError("You can only update your own reviews")

            if update_dto.rating is not None and not (1 <= update_dto.rating <= 5):
                raise ValidationError("Rating must be between 1 and 5")

            updated_review = ReviewMapper.from_update_dto_to_entity(review, update_dto)
            saved_review = await uow.review_repository.update(updated_review)

        return ReviewMapper.from_entity_to_dto(saved_review)

    async def delete_review(self, review_id: UUID, current_user_id: UUID | None = None) -> bool:
        async with self._uow as uow:
            review = await uow.review_repository.get_by_id(review_id)
            if not review:
                raise NotFoundError("Review", str(review_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                customer = await uow.customer_repository.get_by_user_id(current_user_id)
                if not customer or customer.id != review.customer_id:
                    raise PermissionError("You can only delete your own reviews")

            result = await uow.review_repository.delete(review_id)
        return result
