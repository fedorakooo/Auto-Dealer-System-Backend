from datetime import UTC, datetime
from pathlib import Path
from typing import Any
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
    """Creates employee users from the YAML file unless they already exist."""
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

    for index, raw in enumerate(data["employees"], start=1):
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
            logger.warning("Skipping employee entry #%d: missing password in YAML", index)
            continue

        password_plain = str(raw["password"]).strip()
        if not password_plain:
            logger.warning("Skipping employee entry #%d: empty password in YAML", index)
            continue

        existing = await repo.get_by_email(email)
        if existing:
            if existing.role == UserRole.EMPLOYEE:
                await _ensure_employee_profile(db, existing.id, raw, index)
            continue

        hashed = password_handler.hash_password(password_plain)

        user_id: UUID
        if raw.get("id"):
            try:
                user_id = UUID(str(raw["id"]).strip())
            except ValueError:
                logger.warning("Invalid UUID for employee entry #%d, generating a new id", index)
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
            logger.info("Seeded employee user, id: %s", user_id)
        except asyncpg.UniqueViolationError:
            logger.warning(
                "Skipped employee entry #%d: email or phone already exists for another user",
                index,
            )
            continue

        await _ensure_employee_profile(db, user_id, raw, index)


async def _ensure_employee_profile(db: IDatabaseConnection, user_id: UUID, raw: dict[str, Any], index: int) -> None:
    """Binds the employee to a dealership once; an existing profile is never overwritten."""
    if raw.get("dealership_id") is None:
        return
    try:
        dealership_id = int(raw["dealership_id"])
    except (TypeError, ValueError):
        logger.warning("Invalid dealership_id for employee entry #%d", index)
        return

    if await db.fetchval("SELECT 1 FROM employee_profiles WHERE user_id = $1", str(user_id)):
        return
    if not await db.fetchval("SELECT 1 FROM dealerships WHERE id = $1", dealership_id):
        logger.warning(
            "Employee entry #%d: dealership %d does not exist yet, profile will be created on next start",
            index,
            dealership_id,
        )
        return

    position = str(raw.get("position") or "Sales manager").strip()
    await db.execute(
        "INSERT INTO employee_profiles (user_id, dealership_id, position, hire_date) "
        "VALUES ($1, $2, $3, CURRENT_DATE) ON CONFLICT (user_id) DO NOTHING",
        str(user_id),
        dealership_id,
        position,
    )
    logger.info("Seeded employee profile for entry #%d, dealership: %d", index, dealership_id)
