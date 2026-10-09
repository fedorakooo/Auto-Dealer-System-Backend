from src.config import S3Settings
from src.infrastructure.s3.s3_client import S3Client
from src.logger import get_logger

logger = get_logger(__name__)


async def ensure_s3_bucket(s3_settings: S3Settings) -> None:
    if not s3_settings.access_key or not s3_settings.secret_key:
        logger.warning("S3 credentials are not configured; skipping bucket initialization")
        return

    client = S3Client(
        access_key=s3_settings.access_key,
        secret_key=s3_settings.secret_key,
        endpoint=s3_settings.endpoint,
        region_name=s3_settings.region_name,
        bucket_name=s3_settings.bucket_name,
    )
    await client.ensure_bucket_exists()
    logger.info("S3 bucket '%s' is ready", s3_settings.bucket_name)
