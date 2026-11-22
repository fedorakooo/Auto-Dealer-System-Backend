"""Dealership photo gallery: /dealerships/{dealership_id}/media/..."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.dependencies.services import get_dealership_media_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.dealership_media_models import (
    DealershipMediaListResponse,
    DealershipMediaResponse,
    DealershipMediaUpdateRequest,
)
from src.application.abstractions.dealership_media_service import IDealershipMediaService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/dealerships/{dealership_id:int}/media", tags=["dealership-media"])

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Dealership or media not found"}}
AUTH_ERRORS = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
    status.HTTP_403_FORBIDDEN: {"description": "Only an admin or an employee of this dealership"},
}


@router.get("", response_model=DealershipMediaListResponse, responses=NOT_FOUND)
async def list_dealership_media(
    dealership_id: int,
    media_service: Annotated[IDealershipMediaService, Depends(get_dealership_media_service)],
) -> DealershipMediaListResponse:
    """Lists photos of a dealership gallery."""
    media_list = await media_service.get_media_by_dealership(dealership_id)
    return DealershipMediaListResponse(media=[DealershipMediaResponse.from_dto(m) for m in media_list])


@router.post(
    "",
    response_model=DealershipMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or S3 not configured"},
        **AUTH_ERRORS,
        **NOT_FOUND,
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def upload_dealership_media(
    dealership_id: int,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IDealershipMediaService, Depends(get_dealership_media_service)],
    file: UploadFile = File(...),
    description: str | None = Form(None),
    sort_order: int = Form(0),
) -> DealershipMediaResponse:
    """Uploads a photo to a dealership gallery."""
    dto = await media_service.upload_dealership_media_file(
        dealership_id=dealership_id,
        file_content=await file.read(),
        filename=file.filename or "upload",
        requesting_user=requesting_user,
        description=description,
        sort_order=sort_order,
    )
    return DealershipMediaResponse.from_dto(dto)


@router.get("/{media_id:uuid}/file", responses=NOT_FOUND)
async def get_dealership_media_file(
    dealership_id: int,
    media_id: UUID,
    media_service: Annotated[IDealershipMediaService, Depends(get_dealership_media_service)],
) -> StreamingResponse:
    """Streams the file of a dealership photo."""
    body, content_type = await media_service.get_dealership_media_file(dealership_id, media_id)
    return StreamingResponse(body, media_type=content_type)


@router.patch(
    "/{media_id:uuid}",
    response_model=DealershipMediaResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_dealership_media(
    dealership_id: int,
    media_id: UUID,
    body: DealershipMediaUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IDealershipMediaService, Depends(get_dealership_media_service)],
) -> DealershipMediaResponse:
    """Updates metadata of a dealership photo."""
    dto = await media_service.update_dealership_media(dealership_id, media_id, body.to_dto(), requesting_user)
    return DealershipMediaResponse.from_dto(dto)


@router.delete(
    "/{media_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_dealership_media(
    dealership_id: int,
    media_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IDealershipMediaService, Depends(get_dealership_media_service)],
) -> None:
    """Deletes a dealership photo."""
    await media_service.delete_dealership_media(dealership_id, media_id, requesting_user)
