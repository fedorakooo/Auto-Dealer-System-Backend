from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.services import get_vehicle_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.vehicle_models import (
    VehicleCreateRequest,
    VehicleResponse,
    VehiclesResponse,
    VehicleUpdateRequest,
)
from src.application.services.vehicle_service import VehicleService
from src.domain.entities.user import User
from src.domain.value_objects.filters import OrderField, VehicleFilter, VehicleSortField
from src.domain.value_objects.user_role import UserRole
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Model or dealership not found"},
        status.HTTP_409_CONFLICT: {"description": "Vehicle with given VIN already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_vehicle(
    body: VehicleCreateRequest,
    requesting_user: User = Depends(get_current_user),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleResponse:
    logger.info(f"Creating vehicle: VIN={body.vin}, requested by user_id={requesting_user.id}")
    dto = await vehicle_service.create_vehicle(body.to_dto())
    logger.info(f"Vehicle created successfully: id={dto.id}, VIN={body.vin}")
    return VehicleResponse.from_dto(dto)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_vehicle(
    vehicle_id: UUID,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleResponse:
    logger.debug(f"Getting vehicle with id: {vehicle_id}")
    dto = await vehicle_service.get_vehicle(vehicle_id)
    return VehicleResponse.from_dto(dto)


@router.get(
    "",
    response_model=VehiclesResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def list_vehicles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: VehicleSortField | None = Query(None),
    order_by: OrderField = Query(OrderField.ASC),
    model_id: UUID | None = Query(None),
    dealership_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehiclesResponse:
    vehicle_filter = VehicleFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=order_by,
        model_id=str(model_id) if model_id else None,
        dealership_id=dealership_id,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
    )
    vehicles, total = await vehicle_service.get_vehicles(vehicle_filter)
    return VehiclesResponse(
        vehicles=[VehicleResponse.from_dto(v) for v in vehicles],
        total=total,
    )


@router.get(
    "/search",
    response_model=list[VehicleResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def search_vehicles(
    model_name: str | None = Query(None),
    body_type: str | None = Query(None),
    fuel_type: str | None = Query(None),
    transmission_type: str | None = Query(None),
    min_price: float = Query(0, ge=0),
    max_price: float = Query(99999999, ge=0),
    dealership_id: int | None = Query(None),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> list[VehicleResponse]:
    vehicles = await vehicle_service.search_vehicles(
        model_name=model_name,
        body_type=body_type,
        fuel_type=fuel_type,
        transmission_type=transmission_type,
        min_price=min_price,
        max_price=max_price,
        dealership_id=dealership_id,
    )
    return [VehicleResponse.from_dto(v) for v in vehicles]


@router.get(
    "/dealership/{dealership_id}",
    response_model=list[VehicleResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
async def get_vehicles_by_dealership(
    dealership_id: int,
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> list[VehicleResponse]:
    vehicles = await vehicle_service.get_vehicles_by_dealership(dealership_id)
    return [VehicleResponse.from_dto(v) for v in vehicles]


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle, model or dealership not found"},
        status.HTTP_409_CONFLICT: {"description": "Vehicle with given VIN already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_vehicle(
    vehicle_id: UUID,
    body: VehicleUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> VehicleResponse:
    dto = await vehicle_service.update_vehicle(vehicle_id, body.to_dto())
    return VehicleResponse.from_dto(dto)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_vehicle(
    vehicle_id: UUID,
    requesting_user: User = Depends(get_current_user),
    vehicle_service: VehicleService = Depends(get_vehicle_service),
) -> None:
    await vehicle_service.delete_vehicle(vehicle_id)
    return None
