from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_model_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.model_models import (
    ModelCreateRequest,
    ModelResponse,
    ModelsResponse,
    ModelUpdateRequest,
)
from src.application.services.model_service import ModelService
from src.domain.entities.user import User
from src.domain.value_objects.filters import ModelFilter, ModelSortField, OrderField
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/models", tags=["models"])


@router.post(
    "",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Engine or transmission not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_model(
    body: ModelCreateRequest,
    requesting_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    dto = await model_service.create_model(body.to_dto())
    return ModelResponse.from_dto(dto)


@router.get(
    "/{model_id}",
    response_model=ModelResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_model(
    model_id: UUID,
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    dto = await model_service.get_model(model_id)
    return ModelResponse.from_dto(dto)


@router.get(
    "",
    response_model=ModelsResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_models(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: ModelSortField | None = Query(None),
    order_by: OrderField = Query(OrderField.ASC),
    name: str | None = Query(None),
    is_in_production: bool | None = Query(None),
    body_type_id: int | None = Query(None),
    engine_id: int | None = Query(None),
    model_service: ModelService = Depends(get_model_service),
) -> ModelsResponse:
    model_filter = ModelFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=order_by,
        name=name,
        is_in_production=is_in_production,
        body_type_id=body_type_id,
        engine_id=engine_id,
    )
    models, total = await model_service.get_models(model_filter)
    return ModelsResponse(
        models=[ModelResponse.from_dto(m) for m in models],
        total=total,
    )


@router.patch(
    "/{model_id}",
    response_model=ModelResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model, engine or transmission not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_model(
    model_id: UUID,
    body: ModelUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> ModelResponse:
    dto = await model_service.update_model(model_id, body.to_dto())
    return ModelResponse.from_dto(dto)


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_model(
    model_id: UUID,
    requesting_user: User = Depends(get_current_user),
    model_service: ModelService = Depends(get_model_service),
) -> None:
    await model_service.delete_model(model_id)
    return None
