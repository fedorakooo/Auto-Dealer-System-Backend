from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response

from src.api.dependencies.features import require_feature
from src.api.dependencies.services import get_operations_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.operations_models import (
    AddressCreate,
    AppointmentCreate,
    AppointmentStatusUpdate,
    EmployeeProfileCreate,
    OperationResponse,
    OperationsResponse,
    PartReservation,
    PaymentCreate,
    ServiceItemCreate,
    ServiceOrderCreate,
    ServiceStatusUpdate,
)
from src.application.abstractions.operations_service import IOperationsService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(tags=["extended-operations"])


@router.get("/orders/{order_id:uuid}/status-history", response_model=OperationsResponse)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def order_status_history(
    order_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Returns the status history of an order."""
    return OperationsResponse(items=await service.order_history(order_id, limit))


@router.get("/orders/{order_id:uuid}/payments", response_model=OperationsResponse)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def order_payments(
    order_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Lists payments of an order."""
    return OperationsResponse(items=await service.payments(order_id, limit))


@router.post("/orders/{order_id:uuid}/payments", response_model=OperationResponse, status_code=201)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_payment(
    order_id: UUID,
    body: PaymentCreate,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=255)],
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Records a payment for an order."""
    return OperationResponse(
        data=await service.create_payment(order_id, body.model_dump(), idempotency_key, requesting_user.id)
    )


@router.get("/customers/me/addresses", response_model=OperationsResponse)
@PermissionChecker([UserRole.CUSTOMER])
async def addresses(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationsResponse:
    """Lists addresses of the requesting customer."""
    return OperationsResponse(items=await service.addresses(requesting_user.id))


@router.post("/customers/me/addresses", response_model=OperationResponse, status_code=201)
@PermissionChecker([UserRole.CUSTOMER])
async def create_address(
    body: AddressCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Adds an address for the requesting customer."""
    return OperationResponse(data=await service.create_address(requesting_user.id, body.model_dump()))


@router.delete("/customers/me/addresses/{address_id:uuid}", status_code=204)
@PermissionChecker([UserRole.CUSTOMER])
async def delete_address(
    address_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> Response:
    """Deletes an address of the requesting customer."""
    await service.delete_address(requesting_user.id, address_id)
    return Response(status_code=204)


@router.put("/customers/me/addresses/{address_id:uuid}", response_model=OperationResponse)
@PermissionChecker([UserRole.CUSTOMER])
async def update_address(
    address_id: UUID,
    body: AddressCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Replaces an address of the requesting customer."""
    return OperationResponse(data=await service.update_address(requesting_user.id, address_id, body.model_dump()))


@router.get("/employees", response_model=OperationsResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def employee_profiles(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Lists employee profiles."""
    return OperationsResponse(items=await service.employee_profiles(limit))


@router.post("/employees", response_model=OperationResponse, status_code=201)
@PermissionChecker([UserRole.ADMIN])
async def create_employee_profile(
    body: EmployeeProfileCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Creates an employee profile."""
    return OperationResponse(data=await service.create_employee_profile(body.model_dump()))


@router.get("/service/catalog", response_model=OperationsResponse)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def service_catalog(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(100, ge=1, le=100),
) -> OperationsResponse:
    """Lists services offered by the service department."""
    return OperationsResponse(items=await service.catalog(limit))


@router.post(
    "/service/appointments",
    response_model=OperationResponse,
    status_code=201,
    dependencies=[Depends(require_feature("service_appointments"))],
)
@PermissionChecker([UserRole.CUSTOMER])
async def create_appointment(
    body: AppointmentCreate,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=255)],
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Books a service appointment for the requesting customer."""
    return OperationResponse(
        data=await service.create_appointment(requesting_user.id, body.model_dump(), idempotency_key)
    )


@router.get(
    "/service/appointments",
    response_model=OperationsResponse,
    dependencies=[Depends(require_feature("service_appointments"))],
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def appointments(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Lists service appointments visible to the requesting user."""
    user_id = requesting_user.id if requesting_user.role == UserRole.CUSTOMER else None
    return OperationsResponse(items=await service.appointments(user_id, limit))


@router.patch(
    "/service/appointments/{appointment_id:uuid}/status",
    response_model=OperationResponse,
    dependencies=[Depends(require_feature("service_appointments"))],
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def change_appointment_status(
    appointment_id: UUID,
    body: AppointmentStatusUpdate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Changes the status of a service appointment."""
    return OperationResponse(data=await service.change_appointment_status(appointment_id, body.status))


@router.delete(
    "/service/appointments/{appointment_id:uuid}",
    status_code=204,
    dependencies=[Depends(require_feature("service_appointments"))],
)
@PermissionChecker([UserRole.CUSTOMER])
async def delete_appointment(
    appointment_id: UUID,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> Response:
    """Cancels a service appointment of the requesting customer."""
    await service.delete_appointment(requesting_user.id, appointment_id)
    return Response(status_code=204)


@router.post("/service/orders", response_model=OperationResponse, status_code=201)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_service_order(
    body: ServiceOrderCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Creates a service order."""
    return OperationResponse(data=await service.create_service_order(body.model_dump()))


@router.get("/service/orders", response_model=OperationsResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def service_orders(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(50, ge=1, le=100),
) -> OperationsResponse:
    """Lists service orders."""
    return OperationsResponse(items=await service.service_orders(limit))


@router.post("/service/orders/{order_id:uuid}/items", response_model=OperationResponse, status_code=201)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def add_service_item(
    order_id: UUID,
    body: ServiceItemCreate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Adds a work or part item to a service order."""
    return OperationResponse(data=await service.add_service_item(order_id, body.model_dump()))


@router.patch("/service/orders/{order_id:uuid}/status", response_model=OperationResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def change_service_order_status(
    order_id: UUID,
    body: ServiceStatusUpdate,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Changes the status of a service order."""
    return OperationResponse(data=await service.change_service_status(order_id, body.status))


@router.get("/dealerships/{dealership_id}/inventory", response_model=OperationsResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def inventory(
    dealership_id: int,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    below_reorder: bool = False,
    limit: int = Query(100, ge=1, le=100),
) -> OperationsResponse:
    """Lists spare-part inventory of a dealership."""
    return OperationsResponse(items=await service.inventory(dealership_id, below_reorder, limit))


@router.get("/parts", response_model=OperationsResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def spare_parts(
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
    limit: int = Query(100, ge=1, le=100),
) -> OperationsResponse:
    """Lists the spare-part catalog."""
    return OperationsResponse(items=await service.spare_parts(limit))


@router.post("/dealerships/{dealership_id}/inventory/{part_id:uuid}/reservations", response_model=OperationResponse)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def reserve_part(
    dealership_id: int,
    part_id: UUID,
    body: PartReservation,
    requesting_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[IOperationsService, Depends(get_operations_service)],
) -> OperationResponse:
    """Reserves a spare part from a dealership inventory."""
    return OperationResponse(data=await service.reserve_part(dealership_id, part_id, body.quantity))
