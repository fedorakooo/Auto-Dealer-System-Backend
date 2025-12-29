class OrderNotFoundError(Exception):
    """Raised when order is not found."""

    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")


class OrderStatusError(Exception):
    """Raised when order status transition is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class OrderCannotBeCancelledError(OrderStatusError):
    """Raised when order cannot be cancelled."""

    def __init__(self, order_id: str, current_status: str):
        self.order_id = order_id
        self.current_status = current_status
        super().__init__(f"Order with id {order_id} cannot be cancelled from status {current_status}")
