from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_feature_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.feature_models import (
    FeatureAttachRequest,
    FeatureCreateRequest,
    FeatureDetachRequest,
    FeatureResponse,
    FeaturesResponse,
    FeatureUpdateRequest,
)
from src.application.services.feature_service import FeatureService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/features", tags=["features"])


@router.post(
    "",
    response_model=FeatureResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_feature(
    body: FeatureCreateRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeatureResponse:
    dto = await feature_service.create_feature(body.to_dto())
    return FeatureResponse.from_dto(dto)


@router.get(
    "/{feature_id}",
    response_model=FeatureResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_feature(
    feature_id: int,
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeatureResponse:
    dto = await feature_service.get_feature(feature_id)
    return FeatureResponse.from_dto(dto)


@router.get(
    "",
    response_model=FeaturesResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_features(
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeaturesResponse:
    features = await feature_service.get_all_features()
    return FeaturesResponse(features=[FeatureResponse.from_dto(f) for f in features])


@router.get(
    "/model/{model_id}",
    response_model=FeaturesResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_features_by_model(
    model_id: UUID,
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeaturesResponse:
    features = await feature_service.get_features_by_model(model_id)
    return FeaturesResponse(features=[FeatureResponse.from_dto(f) for f in features])


@router.get(
    "/custom-order/{custom_order_id}",
    response_model=FeaturesResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_features_by_custom_order(
    custom_order_id: UUID,
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeaturesResponse:
    features = await feature_service.get_features_by_custom_order(custom_order_id)
    return FeaturesResponse(features=[FeatureResponse.from_dto(f) for f in features])


@router.patch(
    "/{feature_id}",
    response_model=FeatureResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_feature(
    feature_id: int,
    body: FeatureUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> FeatureResponse:
    dto = await feature_service.update_feature(feature_id, body.to_dto())
    return FeatureResponse.from_dto(dto)


@router.delete(
    "/{feature_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_feature(
    feature_id: int,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> None:
    await feature_service.delete_feature(feature_id)
    return None


@router.post(
    "/model/{model_id}/attach",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Feature already attached"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model or feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def attach_feature_to_model(
    model_id: UUID,
    body: FeatureAttachRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> None:
    await feature_service.attach_feature_to_model(model_id, body.to_dto())
    return None


@router.post(
    "/model/{model_id}/detach",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model or feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def detach_feature_from_model(
    model_id: UUID,
    body: FeatureDetachRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> None:
    await feature_service.detach_feature_from_model(model_id, body.to_dto())
    return None


@router.post(
    "/custom-order/{custom_order_id}/attach",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Feature already attached"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order or feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def attach_feature_to_custom_order(
    custom_order_id: UUID,
    body: FeatureAttachRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> None:
    await feature_service.attach_feature_to_custom_order(custom_order_id, body.to_dto())
    return None


@router.post(
    "/custom-order/{custom_order_id}/detach",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Custom order or feature not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def detach_feature_from_custom_order(
    custom_order_id: UUID,
    body: FeatureDetachRequest,
    requesting_user: User = Depends(get_current_user),
    feature_service: FeatureService = Depends(get_feature_service),
) -> None:
    await feature_service.detach_feature_from_custom_order(custom_order_id, body.to_dto())
    return None
