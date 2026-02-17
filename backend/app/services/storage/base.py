"""
Abstract base class for storage providers.
This enables swapping storage backends via dependency injection.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Abstract storage provider interface."""

    @abstractmethod
    async def upload_file(
        self, file: BinaryIO, file_path: str, content_type: str
    ) -> str:
        """
        Upload a file to storage.
        
        Args:
            file: File object to upload
            file_path: Destination path for the file
            content_type: MIME type of the file
            
        Returns:
            str: Storage path or URL of the uploaded file
        """
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            bytes: File content
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            bool: True if deletion was successful
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            bool: True if file exists
        """
        pass

