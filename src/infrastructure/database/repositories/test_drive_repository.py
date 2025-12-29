import logging
from datetime import datetime
from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.testdrive_repository import ITestDriveRepository
from src.domain.entities.test_drive_request import TestDriveRequest
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.test_drive_status import TestDriveStatus
from src.infrastructure.database.exceptions import DatabaseNotFoundError

logger = logging.getLogger(__name__)


class TestDriveRepository(ITestDriveRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, test_drive_id: UUID) -> TestDriveRequest | None:
        query = (
            "SELECT id, customer_id, vehicle_id, dealership_id, requested_datetime, status, "
            "notes, created_at, updated_at FROM get_test_drive_with_details($1::UUID, NULL) LIMIT 1"
        )
        row = await self._db.fetchrow(query, str(test_drive_id))
        if not row:
            return None
        return self._row_to_test_drive(row)

    async def get_by_customer_id(self, customer_id: UUID) -> list[TestDriveRequest]:
        query = "SELECT * FROM test_drive_requests WHERE customer_id = $1 ORDER BY requested_datetime DESC"
        rows = await self._db.fetch(query, str(customer_id))
        return [self._row_to_test_drive(row) for row in rows]

    async def get_by_dealership_id(self, dealership_id: int) -> list[TestDriveRequest]:
        query = (
            "SELECT id, customer_id, vehicle_id, dealership_id, requested_datetime, status, "
            "notes, created_at, updated_at FROM get_test_drive_with_details(NULL, $1)"
        )
        rows = await self._db.fetch(query, dealership_id)
        return [self._row_to_test_drive(row) for row in rows]

    async def get_by_vehicle_id(self, vehicle_id: UUID) -> list[TestDriveRequest]:
        query = "SELECT * FROM test_drive_requests WHERE vehicle_id = $1 ORDER BY requested_datetime DESC"
        rows = await self._db.fetch(query, str(vehicle_id))
        return [self._row_to_test_drive(row) for row in rows]

    async def create(self, test_drive: TestDriveRequest) -> TestDriveRequest:
        query = """
            INSERT INTO test_drive_requests (
                id, customer_id, vehicle_id, dealership_id, requested_datetime, status,
                notes, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(test_drive.id),
            str(test_drive.customer_id),
            str(test_drive.vehicle_id),
            test_drive.dealership_id,
            test_drive.requested_datetime,
            test_drive.status.value,
            test_drive.notes,
            test_drive.created_at or datetime.utcnow(),
        )
        return self._row_to_test_drive(row)

    async def process_request(self, customer_id: UUID, vehicle_id: UUID, requested_datetime: datetime) -> UUID:
        logger.info("CALL process_test_drive_request")

        await self._db.execute(
            "CALL process_test_drive_request($1::UUID, $2::UUID, $3::TIMESTAMPTZ)",
            str(customer_id),
            str(vehicle_id),
            requested_datetime,
        )

        query = """
            SELECT id FROM test_drive_requests
            WHERE customer_id = $1::UUID AND vehicle_id = $2::UUID AND requested_datetime = $3::TIMESTAMPTZ
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = await self._db.fetchval(query, str(customer_id), str(vehicle_id), requested_datetime)
        if not result:
            raise DatabaseNotFoundError("Failed to retrieve created test drive request")
        return parse_uuid(result)

    async def update(self, test_drive: TestDriveRequest) -> TestDriveRequest:
        query = """
            UPDATE test_drive_requests
            SET customer_id = $2, vehicle_id = $3, dealership_id = $4, requested_datetime = $5,
                status = $6, notes = $7, updated_at = $8
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(
            query,
            str(test_drive.id),
            str(test_drive.customer_id),
            str(test_drive.vehicle_id),
            test_drive.dealership_id,
            test_drive.requested_datetime,
            test_drive.status.value,
            test_drive.notes,
            datetime.utcnow(),
        )
        if not row:
            raise DatabaseNotFoundError(f"TestDriveRequest with id {test_drive.id} not found")
        return self._row_to_test_drive(row)

    async def update_status(self, test_drive_id: UUID, new_status: TestDriveStatus) -> TestDriveRequest:
        query = """
            UPDATE test_drive_requests
            SET status = $2, updated_at = $3
            WHERE id = $1
            RETURNING *
        """
        row = await self._db.fetchrow(query, str(test_drive_id), new_status.value, datetime.utcnow())
        if not row:
            raise DatabaseNotFoundError(f"TestDriveRequest with id {test_drive_id} not found")
        return self._row_to_test_drive(row)

    async def delete(self, test_drive_id: UUID) -> bool:
        query = "DELETE FROM test_drive_requests WHERE id = $1"
        result = await self._db.execute(query, str(test_drive_id))
        return result == "DELETE 1"

    def _row_to_test_drive(self, row: asyncpg.Record) -> TestDriveRequest:
        return TestDriveRequest(
            id=parse_uuid(row["id"]),
            customer_id=parse_uuid(row["customer_id"]),
            vehicle_id=parse_uuid(row["vehicle_id"]),
            dealership_id=row["dealership_id"],
            requested_datetime=row["requested_datetime"],
            status=TestDriveStatus(row["status"]),
            notes=row.get("notes"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
