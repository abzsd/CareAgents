"""
Onboarding Routes
Handles user onboarding for patients and doctors
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import asyncpg

from database.postgresql.connection import get_postgresql_pool
from services.onboarding_service import OnboardingService
from models.patient import Address, EmergencyContact, InsuranceInfo


router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class PatientOnboardingRequest(BaseModel):
    """Request model for patient onboarding"""
    user_id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []
    address: Optional[Address] = None
    emergency_contact: Optional[EmergencyContact] = None
    insurance_info: Optional[InsuranceInfo] = None


class DoctorEducation(BaseModel):
    """Doctor education record"""
    degree: str
    institution: str
    year: Optional[int] = None


class DoctorCertification(BaseModel):
    """Doctor certification record"""
    name: str
    issuer: str
    year: Optional[int] = None


class DoctorOnboardingRequest(BaseModel):
    """Request model for doctor onboarding"""
    user_id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    specialization: str
    license_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    experience_years: Optional[int] = None
    address: Optional[Address] = None
    education: Optional[List[DoctorEducation]] = []
    certifications: Optional[List[DoctorCertification]] = []


async def get_onboarding_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> OnboardingService:
    """Dependency to get onboarding service"""
    return OnboardingService(pool)


@router.post("/patient", status_code=status.HTTP_201_CREATED)
async def onboard_patient(
    request: PatientOnboardingRequest,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """
    Onboard a patient user.
    Creates a patient record and links it to the user account.

    Args:
        request: Patient onboarding data

    Returns:
        Patient record and success message
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        data = request.model_dump(exclude_none=True)

        # Extract user_id
        user_id = data.pop('user_id')

        # Call onboarding service
        result = await service.onboard_patient(user_id, **data)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to onboard patient: {str(e)}"
        )


@router.post("/doctor", status_code=status.HTTP_201_CREATED)
async def onboard_doctor(
    request: DoctorOnboardingRequest,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """
    Onboard a doctor user.
    Creates a doctor record and links it to the user account.

    Args:
        request: Doctor onboarding data

    Returns:
        Doctor record and success message
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        data = request.model_dump(exclude_none=True)

        # Extract user_id
        user_id = data.pop('user_id')

        # Convert education and certifications to dicts if they exist
        if 'education' in data and data['education']:
            data['education'] = [edu.dict() if hasattr(edu, 'dict') else edu for edu in data['education']]

        if 'certifications' in data and data['certifications']:
            data['certifications'] = [cert.dict() if hasattr(cert, 'dict') else cert for cert in data['certifications']]

        # Call onboarding service
        result = await service.onboard_doctor(user_id, **data)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to onboard doctor: {str(e)}"
        )


@router.get("/status/{user_id}")
async def check_onboarding_status(
    user_id: str,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """
    Check onboarding status for a user.

    Args:
        user_id: User ID

    Returns:
        Onboarding status and profile data if available
    """
    try:
        result = await service.check_onboarding_status(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check onboarding status: {str(e)}"
        )
