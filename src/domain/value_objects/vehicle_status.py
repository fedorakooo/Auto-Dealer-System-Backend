from enum import StrEnum


class VehicleStatus(StrEnum):
    """Lifecycle status of a vehicle."""

    IN_STOCK = "in_stock"
    RESERVED = "reserved"
    SOLD = "sold"
    SERVICE = "service"
    UNAVAILABLE = "unavailable"


# RESERVED and SOLD are driven by orders and cannot be set by hand.
MANUAL_VEHICLE_STATUSES = frozenset({VehicleStatus.IN_STOCK, VehicleStatus.SERVICE, VehicleStatus.UNAVAILABLE})
