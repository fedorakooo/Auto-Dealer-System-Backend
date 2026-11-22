class TrimInUseError(Exception):
    """Raised when a trim cannot be deleted because vehicles or custom orders reference it."""

    def __init__(self, trim_id: str) -> None:
        self.trim_id = trim_id
        super().__init__(f"Trim with id {trim_id} is referenced by vehicles or custom orders")
