from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_trim_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.trim_models import (
    TrimCreateRequest,
    TrimResponse,
    TrimsResponse,
    TrimUpdateRequest,
)
from src.application.abstractions.trim_service import ITrimService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(tags=["trims"])


@router.get(
    "/models/{model_id:uuid}/trims",
    response_model=TrimsResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Model not found"}},
)
async def list_model_trims(
    model_id: UUID,
    trim_service: Annotated[ITrimService, Depends(get_trim_service)],
) -> TrimsResponse:
    """Lists trims of a model."""
    trims = await trim_service.get_trims_by_model(model_id)
    return TrimsResponse(trims=[TrimResponse.from_dto(t) for t in trims])


@router.post(
    "/models/{model_id:uuid}/trims",
    response_model=TrimResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or duplicate trim name"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model, engine or transmission not found"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_trim(
    model_id: UUID,
    body: TrimCreateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    trim_service: Annotated[ITrimService, Depends(get_trim_service)],
) -> TrimResponse:
    """Creates a trim of a model."""
    dto = await trim_service.create_trim(body.to_dto(model_id))
    return TrimResponse.from_dto(dto)


@router.get(
    "/trims/{trim_id:uuid}",
    response_model=TrimResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Trim not found"}},
)
async def get_trim(
    trim_id: UUID,
    trim_service: Annotated[ITrimService, Depends(get_trim_service)],
) -> TrimResponse:
    """Returns a trim by ID."""
    dto = await trim_service.get_trim(trim_id)
    return TrimResponse.from_dto(dto)


@router.patch(
    "/trims/{trim_id:uuid}",
    response_model=TrimResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or duplicate trim name"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Trim, engine or transmission not found"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_trim(
    trim_id: UUID,
    body: TrimUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    trim_service: Annotated[ITrimService, Depends(get_trim_service)],
) -> TrimResponse:
    """Updates a trim."""
    dto = await trim_service.update_trim(trim_id, body.to_dto())
    return TrimResponse.from_dto(dto)


@router.delete(
    "/trims/{trim_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Trim is used by vehicles or custom orders"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Trim not found"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_trim(
    trim_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    trim_service: Annotated[ITrimService, Depends(get_trim_service)],
) -> None:
    """Deletes a trim that no vehicle or custom order uses."""
    await trim_service.delete_trim(trim_id)
    return None
