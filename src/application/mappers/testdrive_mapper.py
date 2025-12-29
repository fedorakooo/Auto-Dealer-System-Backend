from datetime import datetime
from uuid import uuid4

from src.application.dtos.test_drive_dto import (
    TestDriveCreateDTO,
    TestDriveDTO,
    TestDriveUpdateDTO,
)
from src.domain.entities.test_drive_request import TestDriveRequest
from src.domain.value_objects.test_drive_status import TestDriveStatus


class TestDriveMapper:
    """Mapper for converting between TestDrive DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(test_drive: TestDriveRequest) -> TestDriveDTO:
        return TestDriveDTO(
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

    @staticmethod
    def from_create_dto_to_entity(create_dto: TestDriveCreateDTO) -> TestDriveRequest:
        now = datetime.utcnow()
        return TestDriveRequest(
            id=uuid4(),
            customer_id=create_dto.customer_id,
            vehicle_id=create_dto.vehicle_id,
            dealership_id=create_dto.dealership_id,
            requested_datetime=create_dto.requested_datetime,
            status=TestDriveStatus.REQUESTED,
            notes=create_dto.notes,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        test_drive: TestDriveRequest,
        update_dto: TestDriveUpdateDTO,
    ) -> TestDriveRequest:
        return TestDriveRequest(
            id=test_drive.id,
            customer_id=test_drive.customer_id,
            vehicle_id=update_dto.vehicle_id if update_dto.vehicle_id is not None else test_drive.vehicle_id,
            dealership_id=(
                update_dto.dealership_id if update_dto.dealership_id is not None else test_drive.dealership_id
            ),
            requested_datetime=(
                update_dto.requested_datetime
                if update_dto.requested_datetime is not None
                else test_drive.requested_datetime
            ),
            status=update_dto.status if update_dto.status is not None else test_drive.status,
            notes=update_dto.notes if update_dto.notes is not None else test_drive.notes,
            created_at=test_drive.created_at,
            updated_at=datetime.utcnow(),
        )
