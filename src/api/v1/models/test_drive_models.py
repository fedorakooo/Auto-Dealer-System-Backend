"""Pydantic models for test drive API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.application.dtos.test_drive_dto import (
    TestDriveCreateDTO,
    TestDriveDTO,
    TestDriveUpdateDTO,
)
from src.domain.value_objects.test_drive_status import TestDriveStatus


class TestDriveCreateRequest(BaseModel):
    """Request body for creating a test drive request."""

    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    requested_datetime: datetime
    notes: str | None = None

    def to_dto(self) -> TestDriveCreateDTO:
        return TestDriveCreateDTO(
            customer_id=self.customer_id,
            vehicle_id=self.vehicle_id,
            dealership_id=self.dealership_id,
            requested_datetime=self.requested_datetime,
            notes=self.notes,
        )


class TestDriveUpdateRequest(BaseModel):
    """Request body for updating a test drive request."""

    vehicle_id: UUID | None = None
    dealership_id: int | None = None
    requested_datetime: datetime | None = None
    status: TestDriveStatus | None = None
    notes: str | None = None

    def to_dto(self) -> TestDriveUpdateDTO:
        return TestDriveUpdateDTO(
            vehicle_id=self.vehicle_id,
            dealership_id=self.dealership_id,
            requested_datetime=self.requested_datetime,
            status=self.status,
            notes=self.notes,
        )


class TestDriveResponse(BaseModel):
    """Single test drive response model."""

    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    requested_datetime: datetime
    status: TestDriveStatus = TestDriveStatus.REQUESTED
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, test_drive: TestDriveDTO) -> "TestDriveResponse":
        return cls(
            id=test_drive.id,
            customer_id=test_drive.customer_id,
            vehicle_id=test_drive.vehicle_id,
            dealership_id=test_drive.dealership_id,
            requested_datetime=test_drive.requested_datetime,
            status=test_drive.status,
            notes=test_drive.notes,
            created_at=test_drive.created_at,
            updated_at=test_drive.updated_at,
        )


class TestDrivesResponse(BaseModel):
    """List of test drives response."""

    test_drives: list[TestDriveResponse]


class TestDriveStatusUpdateRequest(BaseModel):
    """Request body for updating test drive status."""

    status: TestDriveStatus
