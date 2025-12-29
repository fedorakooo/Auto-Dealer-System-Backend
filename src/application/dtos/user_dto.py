from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.user_role import UserRole


@dataclass
class UserCreateDTO:
    first_name: str
    second_name: str
    phone_number: str
    email: str
    password: str
    role: UserRole


@dataclass
class UserUpdateDTO:
    first_name: str | None = None
    second_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    is_active: bool | None = None


@dataclass
class UserDTO:
    id: UUID
    first_name: str
    second_name: str
    phone_number: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
