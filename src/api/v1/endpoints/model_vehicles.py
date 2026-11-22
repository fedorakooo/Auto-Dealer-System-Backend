"""Vehicles nested in their model: /models/{model_id}/vehicles/..."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.dependencies.services import get_operations_service, get_vehicle_media_service, get_vehicle_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.operations_models import OperationResponse, OperationsResponse, VehicleStatusCreate
from src.api.v1.models.vehicle_media_models import (
    VehicleMediaListResponse,
    VehicleMediaResponse,
    VehicleMediaUpdateRequest,
)
from src.api.v1.models.vehicle_models import (
    VehicleCreateRequest,
    VehicleResponse,
    VehiclesResponse,
    VehicleUpdateRequest,
)
from src.application.abstractions.operations_service import IOperationsService
from src.application.abstractions.vehicle_media_service import IVehicleMediaService
from src.application.abstractions.vehicle_service import IVehicleService
from src.application.exceptions.errors import NotFoundError
from src.domain.entities.user import User
from src.domain.value_objects.filters import OrderField, VehicleFilter, VehicleSortField
from src.domain.value_objects.media_type import MediaType
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.vehicle_status import VehicleStatus
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/models/{model_id:uuid}/vehicles", tags=["vehicles"])

NOT_FOUND = {
    status.HTTP_404_NOT_FOUND: {"description": "Model or vehicle not found, or the vehicle is of another model"}
}
AUTH_ERRORS = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
    status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
}


async def require_model_vehicle(
    model_id: UUID,
    vehicle_id: UUID,
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
) -> None:
    """Reject paths whose vehicle does not belong to the model in the path."""
    await vehicle_service.ensure_vehicle_in_model(model_id, vehicle_id)


async def _require_media_of_vehicle(service: IVehicleMediaService, vehicle_id: UUID, media_id: UUID) -> None:
    media = await service.get_vehicle_media(media_id)
    if media.vehicle_id != vehicle_id:
        raise NotFoundError("Vehicle media", str(media_id))


# --- Vehicles -------------------------------------------------------------------------------------------------------


@router.get("", response_model=VehiclesResponse)
async def list_model_vehicles(
    model_id: UUID,
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: VehicleSortField | None = Query(None),
    order_by: OrderField = Query(OrderField.ASC),
    trim_id: UUID | None = Query(None),
    dealership_id: int | None = Query(None),
    vehicle_status: VehicleStatus | None = Query(None, alias="status"),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
) -> VehiclesResponse:
    """Lists vehicles of a model with filtering and pagination."""
    vehicle_filter = VehicleFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=order_by,
        model_id=model_id,
        trim_id=trim_id,
        dealership_id=dealership_id,
        status=vehicle_status,
        min_price=min_price,
        max_price=max_price,
    )
    vehicles, total = await vehicle_service.get_vehicles(vehicle_filter)
    return VehiclesResponse(vehicles=[VehicleResponse.from_dto(v) for v in vehicles], total=total)


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or the trim belongs to another model"},
        **AUTH_ERRORS,
        status.HTTP_404_NOT_FOUND: {"description": "Model, trim or dealership not found"},
        status.HTTP_409_CONFLICT: {"description": "Vehicle with given VIN already exists"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_model_vehicle(
    model_id: UUID,
    body: VehicleCreateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
) -> VehicleResponse:
    """Creates a vehicle of a model."""
    logger.info(f"Creating vehicle of model {model_id}, requested by user_id={requesting_user.id}")
    dto = await vehicle_service.create_vehicle(model_id, body.to_dto())
    return VehicleResponse.from_dto(dto)


@router.get("/{vehicle_id:uuid}", response_model=VehicleResponse, responses=NOT_FOUND)
async def get_model_vehicle(
    model_id: UUID,
    vehicle_id: UUID,
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
) -> VehicleResponse:
    """Returns a vehicle of a model."""
    dto = await vehicle_service.get_vehicle(model_id, vehicle_id)
    return VehicleResponse.from_dto(dto)


@router.patch(
    "/{vehicle_id:uuid}",
    response_model=VehicleResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or the trim belongs to another model"},
        **AUTH_ERRORS,
        **NOT_FOUND,
        status.HTTP_409_CONFLICT: {"description": "Vehicle with given VIN already exists"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_model_vehicle(
    model_id: UUID,
    vehicle_id: UUID,
    body: VehicleUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
) -> VehicleResponse:
    """Updates a vehicle of a model."""
    dto = await vehicle_service.update_vehicle(model_id, vehicle_id, body.to_dto(), current_user_id=requesting_user.id)
    return VehicleResponse.from_dto(dto)


@router.delete(
    "/{vehicle_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_model_vehicle(
    model_id: UUID,
    vehicle_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
) -> None:
    """Deletes a vehicle of a model."""
    await vehicle_service.delete_vehicle(model_id, vehicle_id)


# --- Lifecycle status and price history ----------------------------------------------------------------------------


@router.get(
    "/{vehicle_id:uuid}/price-history",
    response_model=OperationsResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def vehicle_price_history(
    vehicle_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Returns the price history of a vehicle."""
    return OperationsResponse(items=await service.vehicle_history(vehicle_id, "price", limit))


@router.get(
    "/{vehicle_id:uuid}/status-history",
    response_model=OperationsResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def vehicle_status_history(
    vehicle_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Returns the status history of a vehicle."""
    return OperationsResponse(items=await service.vehicle_history(vehicle_id, "status", limit))


@router.post(
    "/{vehicle_id:uuid}/status",
    response_model=OperationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def add_vehicle_status(
    vehicle_id: UUID,
    body: VehicleStatusCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Records a status change of a vehicle."""
    return OperationResponse(
        data=await service.add_vehicle_status(vehicle_id, body.status, body.reason, requesting_user.id)
    )


# --- Media (photos of this exact vehicle) ---------------------------------------------------------------------------


@router.get(
    "/{vehicle_id:uuid}/media",
    response_model=VehicleMediaListResponse,
    responses=NOT_FOUND,
    dependencies=[Depends(require_model_vehicle)],
)
async def list_vehicle_media(
    vehicle_id: UUID,
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
) -> VehicleMediaListResponse:
    """Lists media of a vehicle."""
    media_list = await media_service.get_media_by_vehicle(vehicle_id)
    return VehicleMediaListResponse(media=[VehicleMediaResponse.from_dto(m) for m in media_list])


@router.post(
    "/{vehicle_id:uuid}/media",
    response_model=VehicleMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error or S3 not configured"},
        **AUTH_ERRORS,
        **NOT_FOUND,
    },
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def upload_vehicle_media(
    vehicle_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
    file: UploadFile = File(...),
    description: str | None = Form(None),
    sort_order: int = Form(0),
) -> VehicleMediaResponse:
    """Uploads a media file to a vehicle."""
    dto = await media_service.upload_vehicle_media_file(
        vehicle_id=vehicle_id,
        file_content=await file.read(),
        filename=file.filename or "upload",
        media_type=MediaType.IMAGE,
        description=description,
        sort_order=sort_order,
    )
    return VehicleMediaResponse.from_dto(dto)


@router.delete(
    "/{vehicle_id:uuid}/media",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.ADMIN])
async def delete_all_vehicle_media(
    vehicle_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
) -> None:
    """Deletes all media of a vehicle."""
    await media_service.delete_all_vehicle_media(vehicle_id)


@router.get(
    "/{vehicle_id:uuid}/media/{media_id:uuid}/file",
    responses=NOT_FOUND,
    dependencies=[Depends(require_model_vehicle)],
)
async def get_vehicle_media_file(
    vehicle_id: UUID,
    media_id: UUID,
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
) -> StreamingResponse:
    """Streams a media file of a vehicle."""
    await _require_media_of_vehicle(media_service, vehicle_id, media_id)
    body, content_type = await media_service.get_vehicle_media_file(media_id)
    return StreamingResponse(body, media_type=content_type)


@router.patch(
    "/{vehicle_id:uuid}/media/{media_id:uuid}",
    response_model=VehicleMediaResponse,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_vehicle_media(
    vehicle_id: UUID,
    media_id: UUID,
    body: VehicleMediaUpdateRequest,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
) -> VehicleMediaResponse:
    """Updates metadata of a vehicle media file."""
    await _require_media_of_vehicle(media_service, vehicle_id, media_id)
    dto = await media_service.update_vehicle_media(media_id, body.to_dto())
    return VehicleMediaResponse.from_dto(dto)


@router.delete(
    "/{vehicle_id:uuid}/media/{media_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**AUTH_ERRORS, **NOT_FOUND},
    dependencies=[Depends(require_model_vehicle)],
)
@PermissionChecker([UserRole.ADMIN])
async def delete_vehicle_media(
    vehicle_id: UUID,
    media_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    media_service: Annotated[IVehicleMediaService, Depends(get_vehicle_media_service)],
) -> None:
    """Deletes a media file of a vehicle."""
    await _require_media_of_vehicle(media_service, vehicle_id, media_id)
    await media_service.delete_vehicle_media(media_id)
