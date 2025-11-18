"""
FastAPI routes for Prescription Parser Agent operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional, Dict, Any
import os
import uuid
from pathlib import Path

from agents.prescription_parser_agent import PrescriptionParserAgent
from services.storage_service import StorageService

router = APIRouter(prefix="/prescription-parser", tags=["prescription-parser"])


def get_prescription_parser_agent() -> PrescriptionParserAgent:
    """Dependency to get prescription parser agent"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API key not configured"
        )
    return PrescriptionParserAgent(api_key)


def get_storage_service() -> StorageService:
    """Dependency to get storage service"""
    return StorageService()


@router.post("/parse-image", status_code=status.HTTP_200_OK)
async def parse_prescription_image(
    file: UploadFile = File(...),
    agent: PrescriptionParserAgent = Depends(get_prescription_parser_agent),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Parse a prescription image and extract structured data.

    Args:
        file: Prescription image file

    Returns:
        Parsed prescription data with structured information
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )

        # Read file content
        file_content = await file.read()

        # Save to temporary file
        temp_dir = Path("/tmp/prescriptions")
        temp_dir.mkdir(exist_ok=True)

        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix or ".jpg"
        temp_file_path = temp_dir / f"{file_id}{file_extension}"

        with open(temp_file_path, "wb") as f:
            f.write(file_content)

        # Parse the prescription
        result = await agent.parse_prescription_image(image_path=str(temp_file_path))

        # Upload to GCS (optional - for persistent storage)
        try:
            gcs_url = await storage.upload_file(
                file_content,
                f"prescriptions/{file_id}{file_extension}",
                file.content_type
            )
            result["gcs_url"] = gcs_url
            result["file_id"] = file_id
        except Exception as e:
            print(f"Warning: Failed to upload to GCS: {e}")
            result["gcs_url"] = None

        # Clean up temp file
        temp_file_path.unlink(missing_ok=True)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse prescription: {str(e)}"
        )


@router.post("/parse-url", status_code=status.HTTP_200_OK)
async def parse_prescription_from_url(
    image_url: str = Form(...),
    agent: PrescriptionParserAgent = Depends(get_prescription_parser_agent)
):
    """
    Parse a prescription from an image URL.

    Args:
        image_url: URL to the prescription image

    Returns:
        Parsed prescription data
    """
    try:
        result = await agent.parse_prescription_image(image_url=image_url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse prescription: {str(e)}"
        )


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_prescription(
    extracted_data: Dict[str, Any],
    medical_context: Optional[Dict[str, Any]] = None,
    agent: PrescriptionParserAgent = Depends(get_prescription_parser_agent)
):
    """
    Validate and correct extracted prescription data.

    Args:
        extracted_data: Previously extracted prescription data
        medical_context: Optional medical context (patient history, allergies, etc.)

    Returns:
        Validation results with corrections and warnings
    """
    try:
        result = await agent.validate_and_correct_prescription(
            extracted_data,
            medical_context
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate prescription: {str(e)}"
        )


@router.post("/convert-to-text", status_code=status.HTTP_200_OK)
async def convert_prescription_to_text(
    prescription_data: Dict[str, Any],
    agent: PrescriptionParserAgent = Depends(get_prescription_parser_agent)
):
    """
    Convert structured prescription data to editable text format.

    Args:
        prescription_data: Structured prescription data

    Returns:
        Human-readable, editable prescription text
    """
    try:
        result = await agent.convert_to_editable_format(prescription_data)
        return {"text": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert prescription: {str(e)}"
        )
