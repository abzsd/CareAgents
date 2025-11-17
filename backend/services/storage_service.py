"""
Google Cloud Storage service for file uploads
"""
from google.cloud import storage
from typing import Optional
import uuid
import os
from datetime import timedelta


class StorageService:
    """Service for managing file uploads to Google Cloud Storage"""

    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize storage service.

        Args:
            bucket_name: GCS bucket name (defaults to env variable)
        """
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "healthcare-prescriptions")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        folder: str = "prescriptions"
    ) -> str:
        """
        Upload a file to Google Cloud Storage.

        Args:
            file_content: File content as bytes
            file_name: Original file name
            content_type: MIME type of the file
            folder: Folder/prefix in the bucket

        Returns:
            Public URL of the uploaded file
        """
        # Generate unique filename
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

        # Create blob and upload
        blob = self.bucket.blob(unique_filename)
        blob.upload_from_string(file_content, content_type=content_type)

        # Make the blob publicly accessible (optional - remove if you want private files)
        # blob.make_public()

        # Return the public URL or generate a signed URL
        return blob.public_url if blob.public_url else self.generate_signed_url(unique_filename)

    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 60) -> str:
        """
        Generate a signed URL for private file access.

        Args:
            blob_name: Name of the blob in the bucket
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL
        """
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        return url

    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Google Cloud Storage.

        Args:
            blob_name: Name of the blob to delete

        Returns:
            True if deletion was successful
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def list_files(self, prefix: str = "") -> list:
        """
        List files in the bucket with optional prefix.

        Args:
            prefix: Prefix/folder to filter files

        Returns:
            List of blob names
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]
