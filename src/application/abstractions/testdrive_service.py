from abc import ABC, abstractmethod
from uuid import UUID

from src.application.dtos.test_drive_dto import TestDriveCreateDTO, TestDriveDTO, TestDriveUpdateDTO
from src.domain.value_objects.test_drive_status import TestDriveStatus


class ITestDriveService(ABC):
    """Interface for test drive operations."""

    @abstractmethod
    async def create_test_drive(self, create_dto: TestDriveCreateDTO) -> TestDriveDTO:
        """Create a new test drive request."""
        pass

    @abstractmethod
    async def get_test_drive(self, test_drive_id: UUID) -> TestDriveDTO:
        """Get test drive by ID."""
        pass

    @abstractmethod
    async def get_test_drives_by_customer(self, customer_id: UUID) -> list[TestDriveDTO]:
        """Get test drives by customer ID."""
        pass

    @abstractmethod
    async def get_test_drives_by_dealership(self, dealership_id: int) -> list[TestDriveDTO]:
        """Get test drives by dealership ID."""
        pass

    @abstractmethod
    async def get_test_drives_by_vehicle(self, vehicle_id: UUID) -> list[TestDriveDTO]:
        """Get test drives by vehicle ID."""
        pass

    @abstractmethod
    async def update_test_drive(
        self,
        test_drive_id: UUID,
        update_dto: TestDriveUpdateDTO,
        current_user_id: UUID | None = None,
    ) -> TestDriveDTO:
        """Update test drive."""
        pass

    @abstractmethod
    async def update_test_drive_status(
        self,
        test_drive_id: UUID,
        new_status: TestDriveStatus,
        current_user_id: UUID | None = None,
    ) -> TestDriveDTO:
        """Update test drive status."""
        pass

    @abstractmethod
    async def delete_test_drive(
        self,
        test_drive_id: UUID,
        current_user_id: UUID | None = None,
    ) -> bool:
        """Delete test drive."""
        pass
