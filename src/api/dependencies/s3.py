from src.config import settings
from src.domain.abstractions.s3.s3_client import IS3Client
from src.infrastructure.s3.s3_client import S3Client


def get_s3_client() -> IS3Client | None:
    """Get S3 client instance."""
    s3_settings = settings.s3_settings
    if not s3_settings.access_key or not s3_settings.secret_key:
        return None

    return S3Client(
        access_key=s3_settings.access_key,
        secret_key=s3_settings.secret_key,
        endpoint=s3_settings.endpoint,
        region_name=s3_settings.region_name,
        bucket_name=s3_settings.bucket_name,
    )
