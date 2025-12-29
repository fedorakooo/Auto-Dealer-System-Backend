from dataclasses import dataclass
from enum import StrEnum


class OrderField(StrEnum):
    ASC = "asc"
    DESC = "desc"


class UserSortField(StrEnum):
    CREATED_AT = "created_at"
    EMAIL = "email"
    FIRST_NAME = "first_name"
    SECOND_NAME = "second_name"


class VehicleSortField(StrEnum):
    CREATED_AT = "created_at"
    PRICE = "price"
    PRODUCTION_YEAR = "production_year"


class ModelSortField(StrEnum):
    CREATED_AT = "created_at"
    NAME = "name"
    PRODUCTION_YEAR_START = "production_year_start"


class OrderSortField(StrEnum):
    CREATED_AT = "created_at"
    FINAL_PRICE = "final_price"
    STATUS = "status"


@dataclass
class UserFilter:
    page: int = 1
    limit: int = 20
    sort_by: UserSortField | None = None
    order_by: OrderField = OrderField.ASC
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


@dataclass
class VehicleFilter:
    page: int = 1
    limit: int = 20
    sort_by: VehicleSortField | None = None
    order_by: OrderField = OrderField.ASC
    model_id: str | None = None
    dealership_id: int | None = None
    is_active: bool | None = None
    min_price: float | None = None
    max_price: float | None = None


@dataclass
class ModelFilter:
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
    page: int = 1
    limit: int = 20
    sort_by: OrderSortField | None = None
    order_by: OrderField = OrderField.ASC
    customer_id: str | None = None
    dealership_id: int | None = None
    status: str | None = None
