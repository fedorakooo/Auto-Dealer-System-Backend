from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.test_drive_request import TestDriveRequest
from src.domain.value_objects.test_drive_status import TestDriveStatus


class ITestDriveRepository(ABC):
    """Interface for test drive repository operations."""

    @abstractmethod
    async def get_by_id(self, test_drive_id: UUID) -> TestDriveRequest | None:
        """Returns one test drive request by ID or None."""
        pass

    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> list[TestDriveRequest]:
        """Returns test drive requests by customer ID."""
        pass

    @abstractmethod
    async def get_by_dealership_id(self, dealership_id: int) -> list[TestDriveRequest]:
        """Returns test drive requests by dealership ID."""
        pass

    @abstractmethod
    async def get_by_vehicle_id(self, vehicle_id: UUID) -> list[TestDriveRequest]:
        """Returns test drive requests by vehicle ID."""
        pass

    @abstractmethod
    async def create(self, test_drive: TestDriveRequest) -> TestDriveRequest:
        """Creates a new test drive request and returns the created test drive request."""
        pass

    @abstractmethod
    async def process_request(self, customer_id: UUID, vehicle_id: UUID, requested_datetime: datetime) -> UUID:
        """Processes a test drive request and returns the request ID."""
        pass

    @abstractmethod
    async def update(self, test_drive: TestDriveRequest) -> TestDriveRequest:
        """Updates a test drive request and returns the updated test drive request."""
        pass

    @abstractmethod
    async def update_status(self, test_drive_id: UUID, new_status: TestDriveStatus) -> TestDriveRequest:
        """Updates test drive request status and returns the updated test drive request."""
        pass

    @abstractmethod
    async def delete(self, test_drive_id: UUID) -> bool:
        """Deletes a test drive request by its ID."""
        pass
