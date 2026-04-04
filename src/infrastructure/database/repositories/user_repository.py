from datetime import datetime
from uuid import UUID

import asyncpg

from src.config import settings
from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.user_repository import IUserRepository
from src.domain.entities.user import User
from src.domain.utils.uuid_helpers import parse_uuid
from src.domain.value_objects.filters import UserFilter
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.exceptions import DatabaseNotFoundError, DatabaseUniqueViolationError


class UserRepository(IUserRepository):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection

    async def get_by_id(self, user_id: UUID) -> User | None:
        query = "SELECT u.*, c.date_of_birth FROM users u LEFT JOIN customers c ON c.user_id = u.id WHERE u.id = $1"
        row = await self._db.fetchrow(query, str(user_id))
        if not row:
            return None
        return self._row_to_user(row)

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        query = (
            "SELECT u.*, c.date_of_birth FROM users u "
            "LEFT JOIN customers c ON c.user_id = u.id WHERE u.phone_number = $1"
        )
        row = await self._db.fetchrow(query, phone_number)
        if not row:
            return None
        return self._row_to_user(row)

    async def get_by_email(self, email: str) -> User | None:
        query = "SELECT u.*, c.date_of_birth FROM users u LEFT JOIN customers c ON c.user_id = u.id WHERE u.email = $1"
        row = await self._db.fetchrow(query, email)
        if not row:
            return None
        return self._row_to_user(row)

    async def get_users(self, user_filter: UserFilter) -> tuple[list[User], int]:
        offset = (user_filter.page - 1) * user_filter.limit

        sort_by = user_filter.sort_by.value if user_filter.sort_by else "created_at"
        order_direction = user_filter.order_by.value.upper()
        sort_col = sort_by if sort_by in settings.user_list_settings.sort_columns else "created_at"
        order_dir = order_direction if order_direction in ("ASC", "DESC") else "ASC"

        query = f"""
            SELECT
                u.id,
                u.first_name,
                u.second_name,
                u.phone_number,
                u.email,
                u.hashed_password,
                u.role,
                u.is_active,
                u.created_at,
                u.updated_at,
                c.date_of_birth
            FROM users u
            LEFT JOIN customers c ON c.user_id = u.id
            WHERE ($1::varchar IS NULL OR u.email ILIKE '%' || $1::varchar || '%')
              AND ($2::user_role IS NULL OR u.role = $2::user_role)
              AND ($3::boolean IS NULL OR u.is_active = $3::boolean)
            ORDER BY u.{sort_col} {order_dir}
            OFFSET $4::integer LIMIT $5::integer
        """
        rows = await self._db.fetch(
            query,
            user_filter.email,
            user_filter.role,
            user_filter.is_active,
            offset,
            user_filter.limit,
        )

        count_query = """
            SELECT COUNT(*)::bigint
            FROM users u
            WHERE ($1::varchar IS NULL OR u.email ILIKE '%' || $1::varchar || '%')
              AND ($2::user_role IS NULL OR u.role = $2::user_role)
              AND ($3::boolean IS NULL OR u.is_active = $3::boolean)
        """

        total = await self._db.fetchval(
            count_query,
            user_filter.email,
            user_filter.role,
            user_filter.is_active,
        )

        users = [self._row_to_user(row) for row in rows]
        return users, total

    async def create(self, user: User) -> User:
        query = """
            INSERT INTO users (
                id, first_name, second_name, phone_number, email, hashed_password,
                role, is_active, created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(user.id),
                user.first_name,
                user.second_name,
                user.phone_number,
                user.email,
                user.hashed_password,
                user.role.value,
                user.is_active,
                user.created_at or datetime.utcnow(),
            )
            return self._row_to_user(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"User with this email or phone already exists: {exc}") from exc

    async def update(self, user: User) -> User:
        query = """
            UPDATE users
            SET first_name = $2, second_name = $3, phone_number = $4, email = $5,
                hashed_password = $6, role = $7, is_active = $8, updated_at = $9
            WHERE id = $1
            RETURNING *
        """
        try:
            row = await self._db.fetchrow(
                query,
                str(user.id),
                user.first_name,
                user.second_name,
                user.phone_number,
                user.email,
                user.hashed_password,
                user.role.value,
                user.is_active,
                datetime.utcnow(),
            )
            if not row:
                raise DatabaseNotFoundError(f"User with id {user.id} not found")
            return self._row_to_user(row)
        except asyncpg.UniqueViolationError as exc:
            raise DatabaseUniqueViolationError(f"User with this email or phone already exists: {exc}") from exc

    async def delete(self, user_id: UUID) -> bool:
        query = "DELETE FROM users WHERE id = $1"
        result = await self._db.execute(query, str(user_id))
        return result == "DELETE 1"

    def _row_to_user(self, row: asyncpg.Record) -> User:
        return User(
            id=parse_uuid(row["id"]),
            first_name=row["first_name"],
            second_name=row["second_name"],
            phone_number=row["phone_number"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            role=UserRole(row["role"]),
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )
