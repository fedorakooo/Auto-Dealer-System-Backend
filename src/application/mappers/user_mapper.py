from datetime import datetime
from typing import Any
from uuid import uuid4

from src.application.dtos.user_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from src.domain.entities.user import User


class UserMapper:
    """Mapper for converting between User DTOs and Entities."""

    @staticmethod
    def from_entity_to_dto(user: User) -> UserDTO:
        return UserDTO(
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

    @staticmethod
    def from_create_dto_to_entity(create_dto: UserCreateDTO, hashed_password: str) -> User:
        now = datetime.utcnow()
        return User(
            id=uuid4(),
            first_name=create_dto.first_name,
            second_name=create_dto.second_name,
            phone_number=create_dto.phone_number,
            email=create_dto.email,
            hashed_password=hashed_password,
            role=create_dto.role,
            is_active=True,
            created_at=now,
            updated_at=None,
        )

    @staticmethod
    def from_update_dto_to_entity(
        user: User,
        update_dto: UserUpdateDTO,
    ) -> User:
        updated_fields: dict[str, Any] = {}
        if update_dto.first_name is not None:
            updated_fields["first_name"] = update_dto.first_name
        if update_dto.second_name is not None:
            updated_fields["second_name"] = update_dto.second_name
        if update_dto.phone_number is not None:
            updated_fields["phone_number"] = update_dto.phone_number
        if update_dto.email is not None:
            updated_fields["email"] = update_dto.email
        if update_dto.is_active is not None:
            updated_fields["is_active"] = update_dto.is_active

        is_active_value = updated_fields.get("is_active")
        is_active = is_active_value if isinstance(is_active_value, bool) else user.is_active

        return User(
            id=user.id,
            first_name=updated_fields.get("first_name", user.first_name) or user.first_name,
            second_name=updated_fields.get("second_name", user.second_name) or user.second_name,
            phone_number=updated_fields.get("phone_number", user.phone_number) or user.phone_number,
            email=updated_fields.get("email", user.email) or user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=is_active,
            created_at=user.created_at,
            updated_at=datetime.utcnow(),
        )
