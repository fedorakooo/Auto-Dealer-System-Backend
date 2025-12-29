from enum import StrEnum


class CustomOrderStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    CONFIRMED = "confirmed"
    SENT_TO_FACTORY = "sent_to_factory"
    IN_PRODUCTION = "in_production"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
