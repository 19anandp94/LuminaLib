"""MinIO storage provider implementation."""
from typing import BinaryIO

from minio import Minio

from app.services.storage.base import StorageProvider


class MinIOStorageProvider(StorageProvider):
    """MinIO S3-compatible storage implementation."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ):
        """
        Initialize MinIO storage provider.
        
        Args:
            endpoint: MinIO server endpoint
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket: Bucket name
            secure: Use HTTPS
        """
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.bucket = bucket

        # Create bucket if it doesn't exist
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    async def upload_file(
        self, file: BinaryIO, file_path: str, content_type: str
    ) -> str:
        """Upload file to MinIO."""
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Seek back to start

        self.client.put_object(
            self.bucket, file_path, file, file_size, content_type=content_type
        )
        return file_path

    async def download_file(self, file_path: str) -> bytes:
        """Download file from MinIO."""
        response = self.client.get_object(self.bucket, file_path)
        data = response.read()
        response.close()
        response.release_conn()
        return data

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket, file_path)
            return True
        except Exception:
            return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            self.client.stat_object(self.bucket, file_path)
            return True
        except Exception:
            return False

