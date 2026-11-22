from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.dependencies.services import get_vehicle_media_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.vehicle_media_models import (
    VehicleMediaListResponse,
    VehicleMediaResponse,
    VehicleMediaUpdateRequest,
)
from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.domain.entities.user import User
from src.domain.value_objects.media_type import MediaType
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/vehicle-media", tags=["vehicle-media"])


@router.post(
    "/upload",
    response_model=VehicleMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or S3 not configured"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def upload_vehicle_media(
    vehicle_id: UUID = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    sort_order: int = Form(0),
    requesting_user: User = Depends(get_current_user),
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> VehicleMediaResponse:
    content = await file.read()
    filename = file.filename or "upload"
    dto = await vehicle_media_service.upload_vehicle_media_file(
        vehicle_id=vehicle_id,
        file_content=content,
        filename=filename,
        media_type=MediaType.IMAGE,
        description=description,
        sort_order=sort_order,
    )
    return VehicleMediaResponse.from_dto(dto)


@router.get(
    "/vehicle/{vehicle_id}",
    response_model=VehicleMediaListResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_vehicle_media(
    vehicle_id: UUID,
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> VehicleMediaListResponse:
    media_list = await vehicle_media_service.get_media_by_vehicle(vehicle_id)
    return VehicleMediaListResponse(media=[VehicleMediaResponse.from_dto(m) for m in media_list])


@router.get(
    "/{media_id}/file",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_vehicle_media_file(
    media_id: UUID,
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> StreamingResponse:
    body, content_type = await vehicle_media_service.get_vehicle_media_file(media_id)
    return StreamingResponse(body, media_type=content_type)


@router.patch(
    "/{media_id}",
    response_model=VehicleMediaResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_vehicle_media(
    media_id: UUID,
    body: VehicleMediaUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> VehicleMediaResponse:
    dto = await vehicle_media_service.update_vehicle_media(media_id, body.to_dto())
    return VehicleMediaResponse.from_dto(dto)


@router.delete(
    "/vehicle/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_all_vehicle_media(
    vehicle_id: UUID,
    requesting_user: User = Depends(get_current_user),
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> None:
    await vehicle_media_service.delete_all_vehicle_media(vehicle_id)
    return None


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle media not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.ADMIN])
async def delete_vehicle_media(
    media_id: UUID,
    requesting_user: User = Depends(get_current_user),
    vehicle_media_service: IVehicleMediaService = Depends(get_vehicle_media_service),
) -> None:
    await vehicle_media_service.delete_vehicle_media(media_id)
    return None
