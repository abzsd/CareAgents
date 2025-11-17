"""
FastAPI routes for Patient operations using PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
import asyncpg

from database.postgresql.connection import get_postgresql_pool
from services.patient_service import PatientService
from models.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)

router = APIRouter(prefix="/patients", tags=["patients"])


async def get_patient_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> PatientService:
    """Dependency to get patient service"""
    return PatientService(pool)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    service: PatientService = Depends(get_patient_service)
):
    """
    Create a new patient.

    Args:
        patient: Patient data

    Returns:
        Created patient
    """
    try:
        return await service.create_patient(patient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    service: PatientService = Depends(get_patient_service)
):
    """
    Get a patient by ID.

    Args:
        patient_id: Patient ID

    Returns:
        Patient data
    """
    patient = await service.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Only show active patients"),
    service: PatientService = Depends(get_patient_service)
):
    """
    List patients with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        active_only: Only return active patients

    Returns:
        Paginated list of patients
    """
    try:
        result = await service.list_patients(page, page_size, active_only)
        return PatientListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list patients: {str(e)}"
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    service: PatientService = Depends(get_patient_service)
):
    """
    Update a patient.

    Args:
        patient_id: Patient ID
        patient_data: Updated patient data

    Returns:
        Updated patient
    """
    patient = await service.update_patient(patient_id, patient_data)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    service: PatientService = Depends(get_patient_service)
):
    """
    Soft delete a patient (sets is_active to False).

    Args:
        patient_id: Patient ID
    """
    success = await service.delete_patient(patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )


@router.get("/search/", response_model=List[PatientResponse])
async def search_patients(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    service: PatientService = Depends(get_patient_service)
):
    """
    Search patients by name, email, or phone.

    Args:
        q: Search query
        limit: Maximum number of results

    Returns:
        List of matching patients
    """
    try:
        return await service.search_patients(q, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
