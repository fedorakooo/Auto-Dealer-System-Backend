from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.domain.value_objects.fuel_type import FuelType
from src.domain.value_objects.transmission_type import TransmissionType
from src.domain.value_objects.vehicle_status import VehicleStatus


class OrderField(StrEnum):
    """Sort direction."""

    ASC = "asc"
    DESC = "desc"


class UserSortField(StrEnum):
    """Fields the user list can be sorted by."""

    CREATED_AT = "created_at"
    EMAIL = "email"
    FIRST_NAME = "first_name"
    SECOND_NAME = "second_name"


class VehicleSortField(StrEnum):
    """Fields the vehicle list can be sorted by."""

    CREATED_AT = "created_at"
    PRICE = "price"
    PRODUCTION_YEAR = "production_year"


class ModelSortField(StrEnum):
    """Fields the model list can be sorted by."""

    CREATED_AT = "created_at"
    NAME = "name"
    PRODUCTION_YEAR_START = "production_year_start"


class OrderSortField(StrEnum):
    """Fields the order list can be sorted by."""

    CREATED_AT = "created_at"
    FINAL_PRICE = "final_price"
    STATUS = "status"


@dataclass
class UserFilter:
    """Filter and pagination for the user list."""

    page: int = 1
    limit: int = 20
    sort_by: UserSortField | None = None
    order_by: OrderField = OrderField.ASC
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


@dataclass
class VehicleFilter:
    """Filter and pagination for the vehicle list."""

    page: int = 1
    limit: int = 20
    sort_by: VehicleSortField | None = None
    order_by: OrderField = OrderField.ASC
    model_id: UUID | None = None
    trim_id: UUID | None = None
    dealership_id: int | None = None
    status: VehicleStatus | None = None
    min_price: float | None = None
    max_price: float | None = None
    model_name: str | None = None
    body_type: str | None = None
    fuel_type: FuelType | None = None
    transmission_type: TransmissionType | None = None


@dataclass
class ModelFilter:
    """Filter and pagination for the model list."""

    page: int = 1
    limit: int = 20
    sort_by: ModelSortField | None = None
    order_by: OrderField = OrderField.ASC
    name: str | None = None
    is_in_production: bool | None = None
    body_type_id: int | None = None
    engine_id: int | None = None


@dataclass
class OrderFilter:
    """Filter and pagination for the order list."""

    page: int = 1
    limit: int = 20
    sort_by: OrderSortField | None = None
    order_by: OrderField = OrderField.ASC
    customer_id: str | None = None
    dealership_id: int | None = None
    status: str | None = None
