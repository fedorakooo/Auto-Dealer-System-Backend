from abc import ABC, abstractmethod
from io import BytesIO


class IS3Client(ABC):
    """Interface defining the interface for an S3-compatible client."""

    @abstractmethod
    async def get_file(self, key: str) -> tuple[BytesIO, str]:
        """Gets a file from the storage by its key. Returns (body, content_type)."""
        pass

    @abstractmethod
    async def upload_file(self, key: str, file_content: bytes, content_type: str | None = None) -> str:
        """Uploads a file to the storage and returns the key."""
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Deletes a file from the storage by its key."""
        pass

    @abstractmethod
    async def ensure_bucket_exists(self) -> None:
        """Creates the bucket if it does not exist."""
        pass
