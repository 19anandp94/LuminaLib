"""AWS S3 storage provider implementation."""
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.services.storage.base import StorageProvider


class S3StorageProvider(StorageProvider):
    """AWS S3 storage implementation."""

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        bucket: str,
        region: str = "us-east-1",
    ):
        """
        Initialize S3 storage provider.
        
        Args:
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
            bucket: S3 bucket name
            region: AWS region
        """
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        self.bucket = bucket

    async def upload_file(
        self, file: BinaryIO, file_path: str, content_type: str
    ) -> str:
        """Upload file to S3."""
        self.s3_client.upload_fileobj(
            file,
            self.bucket,
            file_path,
            ExtraArgs={"ContentType": content_type},
        )
        return file_path

    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3."""
        response = self.s3_client.get_object(Bucket=self.bucket, Key=file_path)
        return response["Body"].read()

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False

