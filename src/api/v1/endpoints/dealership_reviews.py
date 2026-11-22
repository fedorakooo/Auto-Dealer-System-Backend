"""Dealership reviews, moderation and comment threads: /dealerships/{dealership_id}/reviews/..."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_dealership_review_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user, get_optional_current_user
from src.api.v1.models.dealership_review_models import (
    DealershipReviewCommentCreateRequest,
    DealershipReviewCommentResponse,
    DealershipReviewCreateRequest,
    DealershipReviewResponse,
    DealershipReviewsResponse,
    DealershipReviewUpdateRequest,
    DealershipReviewVisibilityRequest,
)
from src.application.abstractions.dealership_review_service import IDealershipReviewService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/dealerships/{dealership_id:int}/reviews", tags=["dealership-reviews"])

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Dealership, review or comment not found"}}
AUTH_ERRORS = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
    status.HTTP_403_FORBIDDEN: {"description": "Requesting user doesn't have access to this review"},
}
ALL_ROLES = [UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN]


@router.get(
    "",
    response_model=DealershipReviewsResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "include_hidden requires the dealership's staff"},
        **NOT_FOUND,
    },
)
async def list_dealership_reviews(
    dealership_id: int,
    viewer: Annotated[User | None, Depends(get_optional_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    include_hidden: bool = Query(False, description="Also return moderated reviews; staff of the dealership only"),
) -> DealershipReviewsResponse:
    """Lists reviews of a dealership; hidden ones only for staff."""
    page_dto = await review_service.list_reviews(dealership_id, viewer, include_hidden, page, limit)
    return DealershipReviewsResponse.from_dto(page_dto)


@router.post(
    "",
    response_model=DealershipReviewResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or the dealership is already reviewed"},
        **AUTH_ERRORS,
        **NOT_FOUND,
    },
)
@PermissionChecker([UserRole.CUSTOMER])
async def create_dealership_review(
    dealership_id: int,
    body: DealershipReviewCreateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> DealershipReviewResponse:
    """Creates a review of a dealership by the requesting customer."""
    dto = await review_service.create_review(dealership_id, body.to_dto(), requesting_user)
    return DealershipReviewResponse.from_dto(dto)


@router.patch(
    "/{review_id:uuid}",
    response_model=DealershipReviewResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker([UserRole.CUSTOMER])
async def update_dealership_review(
    dealership_id: int,
    review_id: UUID,
    body: DealershipReviewUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> DealershipReviewResponse:
    """Updates the requesting customer's dealership review."""
    dto = await review_service.update_review(dealership_id, review_id, body.to_dto(), requesting_user)
    return DealershipReviewResponse.from_dto(dto)


@router.delete(
    "/{review_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker(ALL_ROLES)
async def delete_dealership_review(
    dealership_id: int,
    review_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> None:
    """Deletes a dealership review."""
    await review_service.delete_review(dealership_id, review_id, requesting_user)


@router.patch(
    "/{review_id:uuid}/visibility",
    response_model=DealershipReviewResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def set_dealership_review_visibility(
    dealership_id: int,
    review_id: UUID,
    body: DealershipReviewVisibilityRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> DealershipReviewResponse:
    """Hides or shows a dealership review (moderation)."""
    dto = await review_service.set_review_visibility(dealership_id, review_id, body.is_hidden, requesting_user)
    return DealershipReviewResponse.from_dto(dto)


@router.post(
    "/{review_id:uuid}/comments",
    response_model=DealershipReviewCommentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker(ALL_ROLES)
async def add_dealership_review_comment(
    dealership_id: int,
    review_id: UUID,
    body: DealershipReviewCommentCreateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> DealershipReviewCommentResponse:
    """Adds a comment to a dealership review."""
    dto = await review_service.add_comment(dealership_id, review_id, body.body, requesting_user)
    return DealershipReviewCommentResponse.from_dto(dto)


@router.delete(
    "/{review_id:uuid}/comments/{comment_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker(ALL_ROLES)
async def delete_dealership_review_comment(
    dealership_id: int,
    review_id: UUID,
    comment_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[IDealershipReviewService, Depends(get_dealership_review_service)],
) -> None:
    """Deletes a comment of a dealership review."""
    await review_service.delete_comment(dealership_id, review_id, comment_id, requesting_user)
