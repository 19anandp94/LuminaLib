"""Local filesystem storage provider implementation."""
import os
from pathlib import Path
from typing import BinaryIO

import aiofiles

from app.services.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: str):
        """
        Initialize local storage provider.
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, file: BinaryIO, file_path: str, content_type: str
    ) -> str:
        """Upload file to local filesystem."""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            content = file.read()
            await f.write(content)

        return str(file_path)

    async def download_file(self, file_path: str) -> bytes:
        """Download file from local filesystem."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self.base_path / file_path

        if full_path.exists():
            os.remove(full_path)
            return True
        return False

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local filesystem."""
        full_path = self.base_path / file_path
        return full_path.exists()

