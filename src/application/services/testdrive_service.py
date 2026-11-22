from datetime import datetime
from uuid import UUID

from src.application.abstractions.testdrive_service import ITestDriveService
from src.application.dtos.test_drive_dto import TestDriveCreateDTO, TestDriveDTO, TestDriveUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.testdrive_mapper import TestDriveMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.test_drive_status import TestDriveStatus
from src.domain.value_objects.user_role import UserRole
from src.domain.value_objects.vehicle_status import VehicleStatus


class TestDriveService(ITestDriveService):
    """Service for test drive operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def _with_model_ids(self, dtos: list[TestDriveDTO]) -> list[TestDriveDTO]:
        """Attach each vehicle's model so clients can build /models/{model_id}/vehicles/{vehicle_id} links."""
        async with self._uow as uow:
            model_ids = await uow.vehicle_repository.get_model_ids(list({dto.vehicle_id for dto in dtos}))
        for dto in dtos:
            dto.model_id = model_ids.get(dto.vehicle_id)
        return dtos

    async def create_test_drive(self, create_dto: TestDriveCreateDTO) -> TestDriveDTO:
        """Create a new test drive request."""
        async with self._uow as uow:
            customer = await uow.customer_repository.get_by_id(create_dto.customer_id)
            if not customer:
                raise NotFoundError("Customer", str(create_dto.customer_id))

            vehicle = await uow.vehicle_repository.get_by_id(create_dto.vehicle_id)
            if not vehicle:
                raise NotFoundError("Vehicle", str(create_dto.vehicle_id))

            if vehicle.status != VehicleStatus.IN_STOCK:
                raise BusinessError("Vehicle is not available for test drive")

            if vehicle.dealership_id != create_dto.dealership_id:
                raise ValidationError("Dealership ID does not match vehicle's dealership")

            if create_dto.requested_datetime <= datetime.utcnow():
                raise ValidationError("Requested datetime must be in the future")

            test_drive_id = await uow.test_drive_repository.process_request(
                customer_id=create_dto.customer_id,
                vehicle_id=create_dto.vehicle_id,
                requested_datetime=create_dto.requested_datetime,
            )

            created_test_drive = await uow.test_drive_repository.get_by_id(test_drive_id)
            if not created_test_drive:
                raise NotFoundError("TestDrive", str(test_drive_id))

            if create_dto.notes:
                created_test_drive.notes = create_dto.notes
                created_test_drive = await uow.test_drive_repository.update(created_test_drive)

        return (await self._with_model_ids([TestDriveMapper.from_entity_to_dto(created_test_drive)]))[0]

    async def get_test_drive(self, test_drive_id: UUID) -> TestDriveDTO:
        """Get test drive by ID."""
        async with self._uow as uow:
            test_drive = await uow.test_drive_repository.get_by_id(test_drive_id)
            if not test_drive:
                raise NotFoundError("TestDrive", str(test_drive_id))
        return (await self._with_model_ids([TestDriveMapper.from_entity_to_dto(test_drive)]))[0]

    async def get_test_drives_by_customer(self, customer_id: UUID) -> list[TestDriveDTO]:
        """Get test drives by customer ID."""
        async with self._uow as uow:
            test_drives = await uow.test_drive_repository.get_by_customer_id(customer_id)
        return await self._with_model_ids([TestDriveMapper.from_entity_to_dto(td) for td in test_drives])

    async def get_test_drives_by_dealership(self, dealership_id: int) -> list[TestDriveDTO]:
        """Get test drives by dealership ID."""
        async with self._uow as uow:
            test_drives = await uow.test_drive_repository.get_by_dealership_id(dealership_id)
        return await self._with_model_ids([TestDriveMapper.from_entity_to_dto(td) for td in test_drives])

    async def get_test_drives_by_vehicle(self, vehicle_id: UUID) -> list[TestDriveDTO]:
        """Get test drives by vehicle ID."""
        async with self._uow as uow:
            test_drives = await uow.test_drive_repository.get_by_vehicle_id(vehicle_id)
        return await self._with_model_ids([TestDriveMapper.from_entity_to_dto(td) for td in test_drives])

    async def update_test_drive(
        self, test_drive_id: UUID, update_dto: TestDriveUpdateDTO, current_user_id: UUID | None = None
    ) -> TestDriveDTO:
        """Update test drive."""
        async with self._uow as uow:
            test_drive = await uow.test_drive_repository.get_by_id(test_drive_id)
            if not test_drive:
                raise NotFoundError("TestDrive", str(test_drive_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    customer = await uow.customer_repository.get_by_user_id(current_user_id)
                    if not customer or customer.id != test_drive.customer_id:
                        raise PermissionError("You can only update your own test drive requests")
                    if test_drive.status != TestDriveStatus.REQUESTED:
                        raise PermissionError("You can only update test drives with REQUESTED status")

            if update_dto.vehicle_id:
                vehicle = await uow.vehicle_repository.get_by_id(update_dto.vehicle_id)
                if not vehicle:
                    raise NotFoundError("Vehicle", str(update_dto.vehicle_id))

            if update_dto.dealership_id:
                dealership = await uow.dealership_repository.get_by_id(update_dto.dealership_id)
                if not dealership:
                    raise NotFoundError("Dealership", str(update_dto.dealership_id))

            if update_dto.requested_datetime and update_dto.requested_datetime <= datetime.utcnow():
                raise ValidationError("Requested datetime must be in the future")

            updated_test_drive = TestDriveMapper.from_update_dto_to_entity(test_drive, update_dto)
            saved_test_drive = await uow.test_drive_repository.update(updated_test_drive)

        return (await self._with_model_ids([TestDriveMapper.from_entity_to_dto(saved_test_drive)]))[0]

    async def update_test_drive_status(
        self, test_drive_id: UUID, new_status: TestDriveStatus, current_user_id: UUID | None = None
    ) -> TestDriveDTO:
        """Update test drive status."""
        async with self._uow as uow:
            test_drive = await uow.test_drive_repository.get_by_id(test_drive_id)
            if not test_drive:
                raise NotFoundError("TestDrive", str(test_drive_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    raise PermissionError("Only employees and admins can change test drive status")

            updated_test_drive = await uow.test_drive_repository.update_status(test_drive_id, new_status)

        return (await self._with_model_ids([TestDriveMapper.from_entity_to_dto(updated_test_drive)]))[0]

    async def delete_test_drive(self, test_drive_id: UUID, current_user_id: UUID | None = None) -> bool:
        """Delete test drive."""
        async with self._uow as uow:
            test_drive = await uow.test_drive_repository.get_by_id(test_drive_id)
            if not test_drive:
                raise NotFoundError("TestDrive", str(test_drive_id))

            if current_user_id:
                current_user = await uow.user_repository.get_by_id(current_user_id)
                if not current_user:
                    raise NotFoundError("User", str(current_user_id))
                if current_user.role not in (UserRole.ADMIN, UserRole.EMPLOYEE):
                    customer = await uow.customer_repository.get_by_user_id(current_user_id)
                    if not customer or customer.id != test_drive.customer_id:
                        raise PermissionError("You can only delete your own test drive requests")
                    if test_drive.status != TestDriveStatus.REQUESTED:
                        raise PermissionError("You can only delete test drives with REQUESTED status")

            result = await uow.test_drive_repository.delete(test_drive_id)
        return result
