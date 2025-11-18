"""
FastAPI routes for Appointment operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from datetime import date
import asyncpg

from database.postgresql.connection import get_postgresql_pool
from services.appointment_service import AppointmentService
from models.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


async def get_appointment_service(pool: asyncpg.Pool = Depends(get_postgresql_pool)) -> AppointmentService:
    """Dependency to get appointment service"""
    return AppointmentService(pool)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Create a new appointment.

    Args:
        appointment: Appointment data

    Returns:
        Created appointment
    """
    try:
        return await service.create_appointment(appointment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get an appointment by ID.

    Args:
        appointment_id: Appointment ID

    Returns:
        Appointment data
    """
    appointment = await service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    return appointment


@router.get("/patient/{patient_id}", response_model=AppointmentListResponse)
async def get_patient_appointments(
    patient_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get all appointments for a patient.

    Args:
        patient_id: Patient ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Filter by status (optional)

    Returns:
        Paginated list of appointments
    """
    try:
        result = await service.get_patient_appointments(patient_id, page, page_size, status)
        return AppointmentListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient appointments: {str(e)}"
        )


@router.get("/doctor/{doctor_id}", response_model=AppointmentListResponse)
async def get_doctor_appointments(
    doctor_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    appointment_date: Optional[date] = Query(None, description="Filter by date"),
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Get all appointments for a doctor.

    Args:
        doctor_id: Doctor ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Filter by status (optional)
        appointment_date: Filter by date (optional)

    Returns:
        Paginated list of appointments
    """
    try:
        result = await service.get_doctor_appointments(
            doctor_id, page, page_size, status, appointment_date
        )
        return AppointmentListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get doctor appointments: {str(e)}"
        )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Update an appointment.

    Args:
        appointment_id: Appointment ID
        appointment_data: Updated appointment data

    Returns:
        Updated appointment
    """
    appointment = await service.update_appointment(appointment_id, appointment_data)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    return appointment


@router.post("/{appointment_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Cancel an appointment.

    Args:
        appointment_id: Appointment ID

    Returns:
        Success message
    """
    success = await service.cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    return {"message": "Appointment cancelled successfully"}


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: str,
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Soft delete an appointment.

    Args:
        appointment_id: Appointment ID
    """
    success = await service.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found"
        )
