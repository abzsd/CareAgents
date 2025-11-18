"""
FastAPI routes for Doctor operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
import asyncpg

from database.postgresql.connection import get_postgresql_pool
from services.doctor_service import DoctorService
from models.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorListResponse
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


async def get_doctor_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> DoctorService:
    """Dependency to get doctor service"""
    return DoctorService(pool)


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: DoctorCreate,
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Create a new doctor.

    Args:
        doctor: Doctor data

    Returns:
        Created doctor
    """
    try:
        return await service.create_doctor(doctor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create doctor: {str(e)}"
        )


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: str,
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Get a doctor by ID.

    Args:
        doctor_id: Doctor ID

    Returns:
        Doctor data
    """
    doctor = await service.get_doctor(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found"
        )
    return doctor


@router.get("/user/{user_id}", response_model=DoctorResponse)
async def get_doctor_by_user_id(
    user_id: str,
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Get a doctor by user ID.

    Args:
        user_id: User ID

    Returns:
        Doctor data
    """
    doctor = await service.get_doctor_by_user_id(user_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with user ID {user_id} not found"
        )
    return doctor


@router.get("/", response_model=DoctorListResponse)
async def list_doctors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    active_only: bool = Query(True, description="Only show active doctors"),
    service: DoctorService = Depends(get_doctor_service)
):
    """
    List doctors with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        specialization: Filter by specialization
        active_only: Only return active doctors

    Returns:
        Paginated list of doctors
    """
    try:
        result = await service.list_doctors(page, page_size, specialization, active_only)
        return DoctorListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list doctors: {str(e)}"
        )


@router.get("/search/", response_model=List[DoctorResponse])
async def search_doctors(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Search doctors by name, specialization, or email.

    Args:
        q: Search query
        limit: Maximum number of results

    Returns:
        List of matching doctors
    """
    try:
        return await service.search_doctors(q, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/specializations/list", response_model=List[str])
async def get_specializations(
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Get list of all unique specializations.

    Returns:
        List of specializations
    """
    try:
        return await service.get_specializations()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get specializations: {str(e)}"
        )


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: str,
    doctor_data: DoctorUpdate,
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Update a doctor.

    Args:
        doctor_id: Doctor ID
        doctor_data: Updated doctor data

    Returns:
        Updated doctor
    """
    doctor = await service.update_doctor(doctor_id, doctor_data)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found"
        )
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: str,
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Soft delete a doctor.

    Args:
        doctor_id: Doctor ID
    """
    success = await service.delete_doctor(doctor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found"
        )
