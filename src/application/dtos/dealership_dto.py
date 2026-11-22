from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class DealershipCreateDTO:
    """Data for creating a dealership."""

    name: str
    address: str
    city_id: int
    phone_number: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True
    description: str | None = None


@dataclass
class DealershipUpdateDTO:
    """Data for updating a dealership."""

    name: str | None = None
    address: str | None = None
    city_id: int | None = None
    phone_number: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool | None = None
    description: str | None = None


@dataclass
class DealershipDTO:
    """Dealership data returned by the application layer."""

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
    description: str | None = None
    updated_at: datetime | None = None
    rating_average: Decimal | None = None
    reviews_count: int = 0
    cover_media_id: UUID | None = None
