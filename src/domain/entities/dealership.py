from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Dealership:
    id: int
    name: str
    address: str
    city_id: int
    phone_number: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True
    updated_at: datetime | None = None
