from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.services import get_test_drive_service
from src.api.rbac import PermissionChecker
from src.api.security import get_current_user
from src.api.v1.models.test_drive_models import (
    TestDriveCreateRequest,
    TestDriveResponse,
    TestDrivesResponse,
    TestDriveStatusUpdateRequest,
    TestDriveUpdateRequest,
)
from src.application.services.testdrive_service import TestDriveService
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole

router = APIRouter(prefix="/test-drives", tags=["test-drives"])


@router.post(
    "",
    response_model=TestDriveResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation or business rule error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Customer, vehicle or dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def create_test_drive(
    body: TestDriveCreateRequest,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDriveResponse:
    dto = await test_drive_service.create_test_drive(body.to_dto())
    return TestDriveResponse.from_dto(dto)


@router.get(
    "/{test_drive_id}",
    response_model=TestDriveResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Test drive not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_test_drive(
    test_drive_id: UUID,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDriveResponse:
    dto = await test_drive_service.get_test_drive(test_drive_id)
    return TestDriveResponse.from_dto(dto)


@router.get(
    "/customer/{customer_id}",
    response_model=TestDrivesResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_test_drives_by_customer(
    customer_id: UUID,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDrivesResponse:
    test_drives = await test_drive_service.get_test_drives_by_customer(customer_id)
    return TestDrivesResponse(test_drives=[TestDriveResponse.from_dto(td) for td in test_drives])


@router.get(
    "/dealership/{dealership_id}",
    response_model=TestDrivesResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_test_drives_by_dealership(
    dealership_id: int,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDrivesResponse:
    test_drives = await test_drive_service.get_test_drives_by_dealership(dealership_id)
    return TestDrivesResponse(test_drives=[TestDriveResponse.from_dto(td) for td in test_drives])


@router.get(
    "/vehicle/{vehicle_id}",
    response_model=TestDrivesResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def get_test_drives_by_vehicle(
    vehicle_id: UUID,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDrivesResponse:
    test_drives = await test_drive_service.get_test_drives_by_vehicle(vehicle_id)
    return TestDrivesResponse(test_drives=[TestDriveResponse.from_dto(td) for td in test_drives])


@router.patch(
    "/{test_drive_id}",
    response_model=TestDriveResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation error"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Test drive, vehicle or dealership not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_test_drive(
    test_drive_id: UUID,
    body: TestDriveUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDriveResponse:
    dto = await test_drive_service.update_test_drive(test_drive_id, body.to_dto(), current_user_id=requesting_user.id)
    return TestDriveResponse.from_dto(dto)


@router.patch(
    "/{test_drive_id}/status",
    response_model=TestDriveResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Test drive not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.EMPLOYEE, UserRole.ADMIN])
async def update_test_drive_status(
    test_drive_id: UUID,
    body: TestDriveStatusUpdateRequest,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> TestDriveResponse:
    dto = await test_drive_service.update_test_drive_status(
        test_drive_id, body.status, current_user_id=requesting_user.id
    )
    return TestDriveResponse.from_dto(dto)


@router.delete(
    "/{test_drive_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid or expired token"},
        status.HTTP_403_FORBIDDEN: {"description": "Requesting user is blocked or doesn't have access to this request"},
        status.HTTP_404_NOT_FOUND: {"description": "Test drive not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected server error"},
    },
)
@PermissionChecker([UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.ADMIN])
async def delete_test_drive(
    test_drive_id: UUID,
    requesting_user: User = Depends(get_current_user),
    test_drive_service: TestDriveService = Depends(get_test_drive_service),
) -> None:
    await test_drive_service.delete_test_drive(test_drive_id, current_user_id=requesting_user.id)
    return None
