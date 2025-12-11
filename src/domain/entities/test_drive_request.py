from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.test_drive_status import TestDriveStatus


@dataclass
class TestDriveRequest:
    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    dealership_id: int
    requested_datetime: datetime
    status: TestDriveStatus = TestDriveStatus.REQUESTED
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
