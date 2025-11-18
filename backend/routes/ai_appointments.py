"""
FastAPI routes for AI-Powered Appointment Booking
Uses Google ADK for intelligent doctor matching and scheduling
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import asyncpg
import os

from database.postgresql.connection import get_postgresql_pool
from services.doctor_service import DoctorService
from services.appointment_service import AppointmentService
from agents.appointment_agent import AppointmentBookingAgent

router = APIRouter(prefix="/ai-appointments", tags=["ai-appointments"])


class DoctorMatchRequest(BaseModel):
    """Request model for AI doctor matching"""
    reason: str
    symptoms: Optional[List[str]] = None
    preferred_specialization: Optional[str] = None


class AppointmentSlotRequest(BaseModel):
    """Request model for AI appointment slot suggestion"""
    doctor_id: str
    patient_preference: Optional[str] = None  # morning, afternoon, evening
    preferred_date: Optional[date] = None


class AppointmentAnalysisRequest(BaseModel):
    """Request model for appointment request analysis"""
    reason: str
    symptoms: Optional[List[str]] = None
    patient_id: Optional[str] = None


def get_ai_agent() -> AppointmentBookingAgent:
    """Get AI appointment agent instance"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API key not configured"
        )
    return AppointmentBookingAgent(api_key)


@router.post("/match-doctor")
async def match_doctor_ai(
    request: DoctorMatchRequest,
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Use AI to match patient with the best doctor based on their needs.

    Args:
        request: Doctor matching request with reason and preferences

    Returns:
        AI-recommended doctor with explanation
    """
    try:
        # Get available doctors
        doctor_service = DoctorService(pool)

        # Get doctors, optionally filtered by specialization
        result = await doctor_service.list_doctors(
            page=1,
            page_size=20,
            specialization=request.preferred_specialization,
            active_only=True
        )

        available_doctors = [doc.model_dump() for doc in result["doctors"]]

        if not available_doctors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No doctors available"
            )

        # Use AI to match doctor
        agent = get_ai_agent()
        recommendation = await agent.match_doctor(
            reason=request.reason,
            symptoms=request.symptoms,
            preferred_specialization=request.preferred_specialization,
            available_doctors=available_doctors
        )

        return recommendation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match doctor: {str(e)}"
        )


@router.post("/suggest-slots")
async def suggest_appointment_slots(
    request: AppointmentSlotRequest,
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Use AI to suggest optimal appointment slots based on doctor availability.

    Args:
        request: Slot suggestion request with doctor ID and preferences

    Returns:
        AI-suggested appointment slots
    """
    try:
        # Get doctor information
        doctor_service = DoctorService(pool)
        doctor = await doctor_service.get_doctor(request.doctor_id)

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID {request.doctor_id} not found"
            )

        # Get doctor's existing appointments
        appointment_service = AppointmentService(pool)
        appointments_result = await appointment_service.get_doctor_appointments(
            doctor_id=request.doctor_id,
            page=1,
            page_size=100,
            status="scheduled"
        )

        existing_appointments = [apt.model_dump() for apt in appointments_result["appointments"]]

        # Get doctor availability (if available in doctor record)
        doctor_availability = doctor.availability if hasattr(doctor, 'availability') and doctor.availability else []

        # Convert DoctorAvailability objects to JSON-compatible dicts
        # Using mode='json' ensures time objects are converted to strings
        doctor_availability_dicts = [
            avail.model_dump(mode='json') if hasattr(avail, 'model_dump') else avail
            for avail in doctor_availability
        ]

        # Use AI to suggest slots
        agent = get_ai_agent()
        suggestions = await agent.suggest_appointment_slots(
            doctor_availability=doctor_availability_dicts,
            existing_appointments=existing_appointments,
            patient_preference=request.patient_preference,
            preferred_date=request.preferred_date
        )

        return suggestions

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suggest slots: {str(e)}"
        )


@router.post("/analyze-request")
async def analyze_appointment_request(
    request: AppointmentAnalysisRequest,
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Use AI to analyze the appointment request and provide insights.

    Args:
        request: Appointment request with reason and symptoms

    Returns:
        AI analysis with urgency, recommended specialization, and suggestions
    """
    try:
        # Optionally get patient's medical history
        medical_history = None
        if request.patient_id:
            # Import medical history service
            from services.medical_history_service import MedicalHistoryService

            history_service = MedicalHistoryService(pool)
            history_result = await history_service.get_patient_medical_history(
                patient_id=request.patient_id,
                page=1,
                page_size=5
            )

            if history_result["records"]:
                # Get the latest records
                medical_history = {
                    "recent_visits": len(history_result["records"]),
                    "latest_diagnosis": history_result["records"][0].diagnosis if history_result["records"] else None,
                    "chronic_conditions": []  # Could be extracted from patient record
                }

        # Use AI to analyze request
        agent = get_ai_agent()
        analysis = await agent.analyze_appointment_request(
            reason=request.reason,
            symptoms=request.symptoms,
            medical_history=medical_history
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze request: {str(e)}"
        )


@router.post("/book-smart")
async def book_appointment_smart(
    patient_id: str,
    reason: str,
    symptoms: Optional[List[str]] = None,
    preferred_specialization: Optional[str] = None,
    patient_preference: Optional[str] = None,
    pool: asyncpg.Pool = Depends(get_postgresql_pool)
):
    """
    Smart appointment booking - uses AI for complete end-to-end booking.

    This endpoint:
    1. Analyzes the appointment request
    2. Matches with the best doctor
    3. Suggests optimal time slots
    4. Creates an appointment request

    Args:
        patient_id: Patient ID
        reason: Reason for consultation
        symptoms: List of symptoms
        preferred_specialization: Preferred doctor specialization
        patient_preference: Time preference (morning/afternoon/evening)

    Returns:
        Complete booking information with doctor match and suggested slots
    """
    try:
        agent = get_ai_agent()

        # Step 1: Analyze the request
        analysis = await agent.analyze_appointment_request(
            reason=reason,
            symptoms=symptoms
        )

        # Step 2: Match with best doctor
        doctor_service = DoctorService(pool)
        spec = preferred_specialization or analysis.get("recommended_specialization")

        result = await doctor_service.list_doctors(
            page=1,
            page_size=20,
            specialization=spec,
            active_only=True
        )

        available_doctors = [doc.model_dump() for doc in result["doctors"]]

        doctor_match = await agent.match_doctor(
            reason=reason,
            symptoms=symptoms,
            preferred_specialization=spec,
            available_doctors=available_doctors
        )

        # Step 3: Suggest appointment slots
        recommended_doctor_id = doctor_match.get("recommended_doctor_id")

        if not recommended_doctor_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No suitable doctor found"
            )

        appointment_service = AppointmentService(pool)
        appointments_result = await appointment_service.get_doctor_appointments(
            doctor_id=recommended_doctor_id,
            page=1,
            page_size=100,
            status="scheduled"
        )

        doctor = await doctor_service.get_doctor(recommended_doctor_id)
        doctor_availability = doctor.availability if hasattr(doctor, 'availability') and doctor.availability else []

        # Convert DoctorAvailability objects to JSON-compatible dicts
        # Using mode='json' ensures time objects are converted to strings
        doctor_availability_dicts = [
            avail.model_dump(mode='json') if hasattr(avail, 'model_dump') else avail
            for avail in doctor_availability
        ]

        slot_suggestions = await agent.suggest_appointment_slots(
            doctor_availability=doctor_availability_dicts,
            existing_appointments=[apt.model_dump() for apt in appointments_result["appointments"]],
            patient_preference=patient_preference
        )

        return {
            "analysis": analysis,
            "doctor_match": doctor_match,
            "suggested_slots": slot_suggestions,
            "next_steps": "Patient can select a slot to confirm the appointment"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to book appointment: {str(e)}"
        )
