from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class VehicleStatusCreate(BaseModel):
    status: Literal["in_stock", "reserved", "sold", "service", "unavailable"]
    reason: str | None = Field(None, max_length=1000)


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: Literal["cash", "bank_card", "bank_transfer", "loan", "lease"]
    status: Literal["pending", "authorized", "paid", "failed", "refunded"] = "paid"
    external_reference: str | None = Field(None, max_length=255)


class AddressCreate(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=20)
    is_default: bool = False


class EmployeeProfileCreate(BaseModel):
    user_id: UUID
    dealership_id: int = Field(gt=0)
    position: str = Field(min_length=1, max_length=100)
    hire_date: date
    status: Literal["active", "vacation", "suspended", "dismissed"] = "active"


class AppointmentCreate(BaseModel):
    dealership_id: int = Field(gt=0)
    vehicle_id: UUID | None = None
    requested_datetime: datetime
    notes: str | None = Field(None, max_length=2000)


class AppointmentStatusUpdate(BaseModel):
    status: Literal["requested", "confirmed", "in_progress", "completed", "cancelled"]


class ServiceOrderCreate(BaseModel):
    appointment_id: UUID | None = None
    customer_id: UUID
    dealership_id: int = Field(gt=0)
    vehicle_id: UUID
    assigned_employee_id: UUID | None = None
    odometer_km: int | None = Field(None, ge=0)


class ServiceItemCreate(BaseModel):
    service_id: int | None = Field(None, gt=0)
    description: str = Field(min_length=1, max_length=255)
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class ServiceStatusUpdate(BaseModel):
    status: Literal["opened", "diagnosis", "in_progress", "waiting_parts", "completed", "cancelled"]


class PartReservation(BaseModel):
    quantity: int = Field(gt=0)


class OperationResponse(BaseModel):
    data: dict[str, Any]


class OperationsResponse(BaseModel):
    items: list[dict[str, Any]]
