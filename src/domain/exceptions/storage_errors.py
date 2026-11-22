class StorageObjectNotFoundError(Exception):
    """Raised when an object is missing from the file storage."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Storage object {key} not found")
