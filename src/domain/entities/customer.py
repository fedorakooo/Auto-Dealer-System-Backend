from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class Customer:
    id: UUID
    user_id: UUID
    date_of_birth: date | None = None
