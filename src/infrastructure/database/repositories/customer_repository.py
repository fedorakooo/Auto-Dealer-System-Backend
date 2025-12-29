from uuid import UUID

import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.customer_repository import ICustomerRepository
from src.domain.entities.customer import Customer
from src.domain.utils.uuid_helpers import parse_uuid
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class CustomerRepository(ICustomerRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        query = "SELECT * FROM customers WHERE id = $1"
        row = await self._db.fetchrow(query, str(customer_id))
        if not row:
            return None
        return self._row_to_customer(row)

    async def get_by_user_id(self, user_id: UUID) -> Customer | None:
        query = "SELECT * FROM customers WHERE user_id = $1"
        row = await self._db.fetchrow(query, str(user_id))
        if not row:
            return None
        return self._row_to_customer(row)

    async def create(self, customer: Customer) -> Customer:
        query = "INSERT INTO customers (id, user_id, date_of_birth) VALUES ($1, $2, $3) RETURNING *" ""
        try:
            row = await self._db.fetchrow(
                query,
                str(customer.id),
                str(customer.user_id),
                customer.date_of_birth,
            )
            return self._row_to_customer(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"Customer with this user_id already exists: {exc}") from exc

    async def update(self, customer: Customer) -> Customer:
        query = "UPDATE customers SET date_of_birth = $2 WHERE id = $1 RETURNING *"
        row = await self._db.fetchrow(query, str(customer.id), customer.date_of_birth)
        if not row:
            raise DatabaseNotFoundError(f"Customer with id {customer.id} not found")
        return self._row_to_customer(row)

    async def delete(self, customer_id: UUID) -> bool:
        query = "DELETE FROM customers WHERE id = $1"
        result = await self._db.execute(query, str(customer_id))
        return result == "DELETE 1"

    def _row_to_customer(self, row: asyncpg.Record) -> Customer:
        return Customer(
            id=parse_uuid(row["id"]),
            user_id=parse_uuid(row["user_id"]),
            date_of_birth=row.get("date_of_birth"),
        )
