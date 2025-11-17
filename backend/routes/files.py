"""
FastAPI routes for File Upload operations using Google Cloud Storage
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form
from typing import Optional
import os

from services.storage_service import StorageService

router = APIRouter(prefix="/files", tags=["files"])


def get_storage_service() -> StorageService:
    """Get storage service instance"""
    return StorageService()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("prescriptions")
):
    """
    Upload a file to Google Cloud Storage.

    Args:
        file: File to upload
        folder: Folder/category for the file (prescriptions, reports, etc.)

    Returns:
        File URL and metadata
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        # Read file content
        file_content = await file.read()

        # Get storage service
        storage_service = get_storage_service()

        # Upload file
        file_url = storage_service.upload_file(
            file_content=file_content,
            file_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            folder=folder
        )

        return {
            "success": True,
            "file_url": file_url,
            "file_name": file.filename,
            "content_type": file.content_type,
            "size": len(file_content)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.delete("/delete/{blob_name:path}")
async def delete_file(blob_name: str):
    """
    Delete a file from Google Cloud Storage.

    Args:
        blob_name: Path to the file in the bucket

    Returns:
        Success status
    """
    try:
        storage_service = get_storage_service()
        success = storage_service.delete_file(blob_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or could not be deleted"
            )

        return {"success": True, "message": "File deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File deletion failed: {str(e)}"
        )


@router.get("/list")
async def list_files(prefix: str = ""):
    """
    List files in the bucket.

    Args:
        prefix: Folder/prefix to filter files

    Returns:
        List of files
    """
    try:
        storage_service = get_storage_service()
        files = storage_service.list_files(prefix=prefix)

        return {
            "success": True,
            "files": files,
            "count": len(files)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )
