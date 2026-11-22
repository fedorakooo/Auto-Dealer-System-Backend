from uuid import UUID

from src.domain.abstractions.database.connection import IDatabaseConnection


async def set_audit_context(db: IDatabaseConnection, user_id: UUID | None, reason: str | None = None) -> None:
    """Tells the history triggers who made the change; the settings last until the transaction ends."""
    await db.execute(
        "SELECT set_config('app.user_id', $1, true), set_config('app.change_reason', $2, true)",
        str(user_id) if user_id else "",
        reason or "",
    )
