from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserSession:
    """Represents an active user session stored in Redis."""
    id: UUID
    user_id: UUID
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
