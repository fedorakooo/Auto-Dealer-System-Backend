from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.dependencies.services import get_model_media_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.model_media_models import (
    ModelMediaListResponse,
    ModelMediaResponse,
    ModelMediaUpdateRequest,
)
from src.application.abstractions.model_media_service import IModelMediaService
from src.domain.entities.user import User
from src.domain.value_objects.media_type import MediaType
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/model-media", tags=["model-media"])


@router.post(
    "/upload",
    response_model=ModelMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or S3 not configured"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def upload_model_media(
    model_id: UUID = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    sort_order: int = Form(0),
    requesting_user: User = Depends(get_current_user),
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> ModelMediaResponse:
    content = await file.read()
    filename = file.filename or "upload"
    dto = await model_media_service.upload_model_media_file(
        model_id=model_id,
        file_content=content,
        filename=filename,
        media_type=MediaType.IMAGE,
        description=description,
        sort_order=sort_order,
    )
    return ModelMediaResponse.from_dto(dto)


@router.get(
    "/model/{model_id}",
    response_model=ModelMediaListResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_model_media(
    model_id: UUID,
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> ModelMediaListResponse:
    media_list = await model_media_service.get_media_by_model(model_id)
    return ModelMediaListResponse(media=[ModelMediaResponse.from_dto(m) for m in media_list])


@router.get(
    "/{media_id}/file",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Model media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_model_media_file(
    media_id: UUID,
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> StreamingResponse:
    body, content_type = await model_media_service.get_model_media_file(media_id)
    return StreamingResponse(body, media_type=content_type)


@router.patch(
    "/{media_id}",
    response_model=ModelMediaResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_model_media(
    media_id: UUID,
    body: ModelMediaUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> ModelMediaResponse:
    dto = await model_media_service.update_model_media(media_id, body.to_dto())
    return ModelMediaResponse.from_dto(dto)


@router.delete(
    "/model/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_all_model_media(
    model_id: UUID,
    requesting_user: User = Depends(get_current_user),
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> None:
    await model_media_service.delete_all_model_media(model_id)
    return None


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_model_media(
    media_id: UUID,
    requesting_user: User = Depends(get_current_user),
    model_media_service: IModelMediaService = Depends(get_model_media_service),
) -> None:
    await model_media_service.delete_model_media(media_id)
    return None
