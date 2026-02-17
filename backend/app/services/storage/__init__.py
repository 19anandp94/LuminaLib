"""
Storage service factory for dependency injection.
Allows swapping storage providers via configuration.
"""
from app.core.config import settings
from app.services.storage.base import StorageProvider
from app.services.storage.local import LocalStorageProvider
from app.services.storage.minio import MinIOStorageProvider
from app.services.storage.s3 import S3StorageProvider


def get_storage_provider() -> StorageProvider:
    """
    Factory function to get the configured storage provider.
    
    This enables swapping storage backends by changing a single config line.
    
    Returns:
        StorageProvider: Configured storage provider instance
    """
    provider = settings.storage_provider.lower()

    if provider == "local":
        return LocalStorageProvider(base_path=settings.storage_local_path)
    elif provider == "minio":
        return MinIOStorageProvider(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            bucket=settings.minio_bucket,
            secure=False,
        )
    elif provider == "s3":
        return S3StorageProvider(
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key,
            bucket=settings.aws_bucket_name,
            region=settings.aws_region,
        )
    else:
        raise ValueError(f"Unknown storage provider: {provider}")


__all__ = ["StorageProvider", "get_storage_provider"]

