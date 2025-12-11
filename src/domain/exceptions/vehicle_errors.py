class VehicleNotFoundError(Exception):
    """Raised when vehicle is not found."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle with id {vehicle_id} not found")


class VehicleNotAvailableError(Exception):
    """Raised when vehicle is not available."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle with id {vehicle_id} is not available")


class VehicleAlreadyOrderedError(Exception):
    """Raised when vehicle is already ordered."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle with id {vehicle_id} is already ordered")
