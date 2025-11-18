"""
Pydantic models for Appointment data
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enum"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Appointment type enum"""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    ROUTINE_CHECKUP = "routine_checkup"
    EMERGENCY = "emergency"
    TELECONSULTATION = "teleconsultation"


class AppointmentBase(BaseModel):
    """Base appointment model"""
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: time
    appointment_type: AppointmentType = AppointmentType.CONSULTATION
    reason: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = Field(30, ge=15, le=180)


class AppointmentCreate(AppointmentBase):
    """Model for creating new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Model for updating appointment"""
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)


class AppointmentResponse(AppointmentBase):
    """Model for appointment response"""
    appointment_id: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "appointment_id": "950e8400-e29b-41d4-a716-446655440000",
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "doctor_id": "650e8400-e29b-41d4-a716-446655440000",
                "patient_name": "John Doe",
                "doctor_name": "Dr. Sarah Johnson",
                "doctor_specialization": "Cardiology",
                "appointment_date": "2025-11-20",
                "appointment_time": "10:30:00",
                "appointment_type": "consultation",
                "status": "scheduled",
                "reason": "Routine checkup",
                "location": "Room 204, Main Building",
                "duration_minutes": 30
            }
        }


class AppointmentListResponse(BaseModel):
    """Model for paginated appointment list"""
    appointments: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
