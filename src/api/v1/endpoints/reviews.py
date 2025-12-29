from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_review_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.review_models import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewsResponse,
    ReviewUpdateRequest,
)
from src.application.services.review_service import ReviewService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer or model not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_review(
    body: ReviewCreateRequest,
    requesting_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    dto = await review_service.create_review(body.to_dto())
    return ReviewResponse.from_dto(dto)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Review not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_review(
    review_id: UUID,
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    dto = await review_service.get_review(review_id)
    return ReviewResponse.from_dto(dto)


@router.get(
    "/model/{model_id}",
    response_model=ReviewsResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_reviews_by_model(
    model_id: UUID,
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewsResponse:
    reviews = await review_service.get_reviews_by_model(model_id)
    return ReviewsResponse(reviews=[ReviewResponse.from_dto(r) for r in reviews])


@router.get(
    "/customer/{customer_id}",
    response_model=ReviewsResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_reviews_by_customer(
    customer_id: UUID,
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewsResponse:
    reviews = await review_service.get_reviews_by_customer(customer_id)
    return ReviewsResponse(reviews=[ReviewResponse.from_dto(r) for r in reviews])


@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Review not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_review(
    review_id: UUID,
    body: ReviewUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    dto = await review_service.update_review(review_id, body.to_dto(), current_user_id=requesting_user.id)
    return ReviewResponse.from_dto(dto)


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Review not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_review(
    review_id: UUID,
    requesting_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
) -> None:
    await review_service.delete_review(review_id, current_user_id=requesting_user.id)
    return None
