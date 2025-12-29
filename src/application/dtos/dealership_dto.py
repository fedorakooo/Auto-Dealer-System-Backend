from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class DealershipCreateDTO:
    name: str
    address: str
    city_id: int
    phone_number: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True


@dataclass
class DealershipUpdateDTO:
    name: str | None = None
    address: str | None = None
    city_id: int | None = None
    phone_number: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool | None = None


@dataclass
class DealershipDTO:
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
