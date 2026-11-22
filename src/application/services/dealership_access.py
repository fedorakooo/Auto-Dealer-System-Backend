"""Who may manage a dealership page: an admin, or an employee whose profile belongs to that dealership."""

from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.entities.user import User
from src.domain.exceptions.auth_errors import ForbiddenError
from src.domain.value_objects.user_role import UserRole


async def get_managed_dealership_id(uow: IUnitOfWork, user: User | None) -> int | None:
    """Returns the employee's own dealership, or None for anyone without an active employee profile."""
    if user is None or user.role != UserRole.EMPLOYEE:
        return None
    return await uow.dealership_repository.get_employee_dealership_id(user.id)


async def can_manage_dealership(uow: IUnitOfWork, user: User | None, dealership_id: int) -> bool:
    """Returns True if the user may manage the dealership page."""
    if user is None:
        return False
    if user.role == UserRole.ADMIN:
        return True
    return await get_managed_dealership_id(uow, user) == dealership_id


async def ensure_can_manage_dealership(uow: IUnitOfWork, user: User | None, dealership_id: int) -> None:
    """Raises ForbiddenError unless the user may manage the dealership page."""
    if not await can_manage_dealership(uow, user, dealership_id):
        raise ForbiddenError()
