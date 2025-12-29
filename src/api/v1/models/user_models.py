"""Pydantic models for user API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from src.application.dtos.user_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from src.domain.value_objects.user_role import UserRole


class UserCreateRequest(BaseModel):
    """Request body for creating a user."""

    first_name: str
    second_name: str
    phone_number: str
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v):
        """Convert role to lowercase if it's a string."""
        # If it's already a UserRole, return it as is
        if isinstance(v, UserRole):
            return v
        # If it's a string, convert to lowercase and validate
        if isinstance(v, str):
            v = v.lower()
            try:
                return UserRole(v)
            except ValueError:
                # If it's not a valid value, raise a more helpful error
                raise ValueError(f"Role must be one of: {', '.join([role.value for role in UserRole])}") from None
        # For any other type, try to convert
        try:
            return UserRole(v)
        except (ValueError, TypeError):
            raise ValueError(f"Role must be one of: {', '.join([role.value for role in UserRole])}") from None

    def to_dto(self) -> UserCreateDTO:
        return UserCreateDTO(
            first_name=self.first_name,
            second_name=self.second_name,
            phone_number=self.phone_number,
            email=str(self.email),
            password=self.password,
            role=self.role,
        )


class UserUpdateRequest(BaseModel):
    """Request body for updating a user."""

    first_name: str | None = None
    second_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None

    def to_dto(self) -> UserUpdateDTO:
        return UserUpdateDTO(
            first_name=self.first_name,
            second_name=self.second_name,
            phone_number=self.phone_number,
            email=str(self.email) if self.email is not None else None,
            is_active=self.is_active,
        )


class UserResponse(BaseModel):
    """Single user response model."""

    id: UUID
    first_name: str
    second_name: str
    phone_number: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_dto(cls, user: UserDTO) -> "UserResponse":
        return cls(
            id=user.id,
            first_name=user.first_name,
            second_name=user.second_name,
            phone_number=user.phone_number,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UsersResponse(BaseModel):
    """Paginated users response."""

    users: list[UserResponse]
    total: int
