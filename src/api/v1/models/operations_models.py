from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class VehicleStatusCreate(BaseModel):
    """Request body for recording a vehicle status change."""

    status: Literal["in_stock", "service", "unavailable"]  # reserved/sold are driven by orders
    reason: str | None = Field(None, max_length=1000)


class PaymentCreate(BaseModel):
    """Request body for recording an order payment."""

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: Literal["cash", "bank_card", "bank_transfer", "loan", "lease"]
    status: Literal["pending", "authorized", "paid", "failed", "refunded"] = "paid"
    external_reference: str | None = Field(None, max_length=255)


class AddressCreate(BaseModel):
    """Request body for a customer address."""

    label: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=20)
    is_default: bool = False


class EmployeeProfileCreate(BaseModel):
    """Request body for creating an employee profile."""

    user_id: UUID
    dealership_id: int = Field(gt=0)
    position: str = Field(min_length=1, max_length=100)
    hire_date: date
    status: Literal["active", "vacation", "suspended", "dismissed"] = "active"


class AppointmentCreate(BaseModel):
    """Request body for booking a service appointment."""

    dealership_id: int = Field(gt=0)
    vehicle_id: UUID | None = None
    requested_datetime: datetime
    notes: str | None = Field(None, max_length=2000)


class AppointmentStatusUpdate(BaseModel):
    """Request body for changing a service appointment status."""

    status: Literal["requested", "confirmed", "in_progress", "completed", "cancelled"]


class ServiceOrderCreate(BaseModel):
    """Request body for creating a service order."""

    appointment_id: UUID | None = None
    customer_id: UUID
    dealership_id: int = Field(gt=0)
    vehicle_id: UUID
    assigned_employee_id: UUID | None = None
    odometer_km: int | None = Field(None, ge=0)


class ServiceItemCreate(BaseModel):
    """Request body for adding an item to a service order."""

    service_id: int | None = Field(None, gt=0)
    description: str = Field(min_length=1, max_length=255)
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class ServiceStatusUpdate(BaseModel):
    """Request body for changing a service order status."""

    status: Literal["opened", "diagnosis", "in_progress", "waiting_parts", "completed", "cancelled"]


class PartReservation(BaseModel):
    """Request body for reserving a spare part."""

    quantity: int = Field(gt=0)


class OperationResponse(BaseModel):
    """Generic single-record response of an operations endpoint."""

    data: dict[str, Any]


class OperationsResponse(BaseModel):
    """Generic list response of an operations endpoint."""

    items: list[dict[str, Any]]
