"""
FastAPI routes for Medical History operations using PostgreSQL
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
import asyncpg

from database.postgresql.connection import get_postgresql_pool
from services.medical_history_service import MedicalHistoryService
from models.medical_history import (
    MedicalHistoryCreate,
    MedicalHistoryUpdate,
    MedicalHistoryResponse,
    MedicalHistoryListResponse
)

router = APIRouter(prefix="/medical-history", tags=["medical-history"])


async def get_medical_history_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> MedicalHistoryService:
    """Dependency to get medical history service"""
    return MedicalHistoryService(pool)


@router.post("/", response_model=MedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_history(
    history: MedicalHistoryCreate,
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Create a new medical history record.

    Args:
        history: Medical history data

    Returns:
        Created medical history record
    """
    try:
        return await service.create_medical_history(history)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create medical history: {str(e)}"
        )


@router.get("/{history_id}", response_model=MedicalHistoryResponse)
async def get_medical_history(
    history_id: str,
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Get a medical history record by ID.

    Args:
        history_id: Medical history ID

    Returns:
        Medical history record
    """
    history = await service.get_medical_history(history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical history with ID {history_id} not found"
        )
    return history


@router.get("/patient/{patient_id}", response_model=MedicalHistoryListResponse)
async def get_patient_medical_history(
    patient_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Get all medical history records for a patient.

    Args:
        patient_id: Patient ID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated list of medical history records
    """
    try:
        result = await service.get_patient_medical_history(patient_id, page, page_size)
        return MedicalHistoryListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient medical history: {str(e)}"
        )


@router.get("/doctor/{doctor_id}/patients")
async def get_doctor_patients(
    doctor_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Get all patients who have medical history with this doctor.

    Args:
        doctor_id: Doctor ID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated list of patients with their latest medical history
    """
    try:
        result = await service.get_doctor_patients_with_history(doctor_id, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get doctor's patients: {str(e)}"
        )


@router.get("/patients/all")
async def get_all_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Get all patients in the system.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated list of all patients
    """
    try:
        result = await service.get_all_patients(page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get all patients: {str(e)}"
        )


@router.put("/{history_id}", response_model=MedicalHistoryResponse)
async def update_medical_history(
    history_id: str,
    history_data: MedicalHistoryUpdate,
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Update a medical history record.

    Args:
        history_id: Medical history ID
        history_data: Updated medical history data

    Returns:
        Updated medical history record
    """
    history = await service.update_medical_history(history_id, history_data)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical history with ID {history_id} not found"
        )
    return history


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_history(
    history_id: str,
    service: MedicalHistoryService = Depends(get_medical_history_service)
):
    """
    Soft delete a medical history record.

    Args:
        history_id: Medical history ID
    """
    success = await service.delete_medical_history(history_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical history with ID {history_id} not found"
        )
