from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.test_drive_status import TestDriveStatus


@dataclass
class TestDriveCreateDTO:
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    requested_datetime: datetime
    notes: str | None = None


@dataclass
class TestDriveUpdateDTO:
    vehicle_id: UUID | None = None
    dealership_id: int | None = None
    requested_datetime: datetime | None = None
    status: TestDriveStatus | None = None
    notes: str | None = None


@dataclass
class TestDriveDTO:
    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    requested_datetime: datetime
    status: TestDriveStatus = TestDriveStatus.REQUESTED
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
