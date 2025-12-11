from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.user_role import UserRole


@dataclass
class User:
    id: UUID
    first_name: str
    second_name: str
    phone_number: str
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
