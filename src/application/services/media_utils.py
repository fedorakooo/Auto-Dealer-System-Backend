import mimetypes
import re

from src.application.exceptions.errors import ValidationError
from src.domain.value_objects.media_type import MediaType

ALLOWED_IMAGE_EXTENSIONS = frozenset({"jpg", "jpeg", "png", "webp"})
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

EXTENSION_TO_MIME = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def sanitize_filename(filename: str) -> str:
    base = filename.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1]
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", base).strip("._")
    return safe or "upload"


def resolve_content_type(filename: str, media_type: MediaType) -> str:
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    if media_type == MediaType.IMAGE:
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            return guessed
        return EXTENSION_TO_MIME.get(extension, "application/octet-stream")
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    return f"video/{extension}" if extension else "application/octet-stream"


def validate_image_upload(filename: str, file_content: bytes) -> None:
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Unsupported image format. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}")
    if len(file_content) > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"Image size exceeds {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB limit")
    if not file_content:
        raise ValidationError("Uploaded file is empty")
