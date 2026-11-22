"""Read-only search across all models; vehicle CRUD lives under /models/{model_id}/vehicles."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies.services import get_vehicle_service
from src.api.v1.models.vehicle_models import VehicleResponse, VehiclesResponse
from src.application.abstractions.vehicle_service import IVehicleService
from src.domain.value_objects.filters import OrderField, VehicleFilter, VehicleSortField
from src.domain.value_objects.fuel_type import FuelType
from src.domain.value_objects.transmission_type import TransmissionType
from src.domain.value_objects.vehicle_status import VehicleStatus

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=VehiclesResponse)
async def search_vehicles(
    vehicle_service: Annotated[IVehicleService, Depends(get_vehicle_service)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: VehicleSortField | None = Query(None),
    order_by: OrderField = Query(OrderField.ASC),
    model_id: UUID | None = Query(None),
    model_name: str | None = Query(None, description="Case-insensitive substring of the model name"),
    body_type: str | None = Query(None, description="Body type name, case-insensitive (e.g. Sedan)"),
    fuel_type: FuelType | None = Query(None),
    transmission_type: TransmissionType | None = Query(None),
    dealership_id: int | None = Query(None),
    vehicle_status: VehicleStatus | None = Query(None, alias="status"),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
) -> VehiclesResponse:
    """Searches vehicles across all models."""
    vehicle_filter = VehicleFilter(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order_by=order_by,
        model_id=model_id,
        model_name=model_name or None,
        body_type=body_type or None,
        fuel_type=fuel_type,
        transmission_type=transmission_type,
        dealership_id=dealership_id,
        status=vehicle_status,
        min_price=min_price,
        max_price=max_price,
    )
    vehicles, total = await vehicle_service.get_vehicles(vehicle_filter)
    return VehiclesResponse(vehicles=[VehicleResponse.from_dto(v) for v in vehicles], total=total)
