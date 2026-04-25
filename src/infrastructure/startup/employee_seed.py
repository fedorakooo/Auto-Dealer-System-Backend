from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import asyncpg
import yaml

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.auth.password_handler import PasswordHandler
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.logger import get_logger

logger = get_logger(__name__)


async def seed_employees_if_missing(db: IDatabaseConnection, employees_path: Path) -> None:
    if not employees_path.is_file():
        logger.debug("Employees seed file not found: %s", employees_path)
        return

    with employees_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or not isinstance(data.get("employees"), list):
        logger.warning("employees.yaml must contain a top-level 'employees' list")
        return

    password_handler = PasswordHandler()
    repo = UserRepository(db)

    for raw in data["employees"]:
        if not isinstance(raw, dict):
            logger.warning("Skipping invalid employee entry (not a mapping)")
            continue

        try:
            email = str(raw["email"]).strip()
            first_name = str(raw["first_name"]).strip()
            second_name = str(raw["second_name"]).strip()
            phone_number = str(raw["phone_number"]).strip()
        except KeyError as exc:
            logger.warning("Skipping employee missing required field: %s", exc)
            continue

        if "password" not in raw or raw["password"] is None:
            logger.warning("Skipping employee %s: missing password in YAML", email)
            continue

        password_plain = str(raw["password"]).strip()
        if not password_plain:
            logger.warning("Skipping employee %s: empty password in YAML", email)
            continue

        if await repo.get_by_email(email):
            continue

        hashed = password_handler.hash_password(password_plain)

        user_id: UUID
        if raw.get("id"):
            try:
                user_id = UUID(str(raw["id"]).strip())
            except ValueError:
                logger.warning("Invalid UUID for employee %s, generating a new id", email)
                user_id = uuid4()
        else:
            user_id = uuid4()

        user = User(
            id=user_id,
            first_name=first_name,
            second_name=second_name,
            phone_number=phone_number,
            email=email,
            hashed_password=hashed,
            role=UserRole.EMPLOYEE,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        try:
            await repo.create(user)
            logger.info("Seeded employee user: %s", email)
        except asyncpg.UniqueViolationError:
            logger.warning(
                "Skipped employee %s: email or phone already exists for another user",
                email,
            )
