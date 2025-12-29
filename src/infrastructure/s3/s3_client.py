from io import BytesIO

import aioboto3
from botocore.config import Config

from src.domain.abstractions.s3.s3_client import IS3Client


class S3Client(IS3Client):
    """A client for interacting with an S3-compatible object storage service."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint: str,
        region_name: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint,
            "region_name": region_name,
            "config": Config(signature_version="s3v4"),
        }
        self.bucket_name = bucket_name
        self.session = aioboto3.Session()

    async def get_file(self, key: str) -> BytesIO:
        async with self.session.client("s3", **self.config) as s3:
            response = await s3.get_object(Bucket=self.bucket_name, Key=key)
            body = await response["Body"].read()
            return BytesIO(body)

    async def upload_file(self, key: str, file_content: bytes, content_type: str | None = None) -> str:
        """Uploads a file to S3 and returns the key."""
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        async with self.session.client("s3", **self.config) as s3:
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                **extra_args,
            )
        return key

    async def delete_file(self, key: str) -> bool:
        """Deletes a file from S3 by its key."""
        try:
            async with self.session.client("s3", **self.config) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
