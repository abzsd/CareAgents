"""
Pydantic models for Medical History data
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class Prescription(BaseModel):
    """Prescription details within medical history"""
    medication_name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None


class MedicalHistoryBase(BaseModel):
    """Base medical history model"""
    patient_id: str
    doctor_id: Optional[str] = None
    doctor_name: str = Field(..., description="Name of the doctor")
    visit_date: date
    diagnosis: Optional[str] = None
    prescriptions: Optional[List[Prescription]] = []
    health_status: Optional[str] = Field(None, description="General health status")
    blood_pressure: Optional[str] = Field(None, description="Blood pressure reading (e.g., '120/80')")
    symptoms: Optional[List[str]] = Field([], description="List of symptoms reported")
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class MedicalHistoryCreate(MedicalHistoryBase):
    """Model for creating new medical history record"""
    pass


class MedicalHistoryUpdate(BaseModel):
    """Model for updating medical history (all fields optional)"""
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_date: Optional[date] = None
    diagnosis: Optional[str] = None
    prescriptions: Optional[List[Prescription]] = None
    health_status: Optional[str] = None
    blood_pressure: Optional[str] = None
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class MedicalHistoryResponse(MedicalHistoryBase):
    """Model for medical history response"""
    history_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "history_id": "850e8400-e29b-41d4-a716-446655440000",
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "doctor_id": "650e8400-e29b-41d4-a716-446655440000",
                "doctor_name": "Dr. Sarah Johnson",
                "visit_date": "2024-01-15",
                "diagnosis": "Common cold with mild fever",
                "prescriptions": [
                    {
                        "medication_name": "Paracetamol",
                        "dosage": "500mg",
                        "frequency": "3 times a day",
                        "duration": "5 days",
                        "instructions": "Take after meals"
                    }
                ],
                "health_status": "Stable",
                "blood_pressure": "120/80",
                "symptoms": ["fever", "headache", "fatigue"],
                "notes": "Rest recommended for 3 days",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }


class MedicalHistoryListResponse(BaseModel):
    """Model for paginated medical history list"""
    records: List[MedicalHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
