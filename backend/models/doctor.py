"""
Pydantic models for Doctor data
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import time, date, datetime


class Qualification(BaseModel):
    """Doctor qualification model"""
    degree: str
    institution: str
    year: Optional[int] = None


class OrganizationAffiliation(BaseModel):
    """Organization affiliation model"""
    organization_id: str
    organization_name: str
    department_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[str] = Field(None, description="full_time, part_time, visiting, consultant")
    joined_date: Optional[date] = None
    is_primary: Optional[bool] = False


class DoctorAvailability(BaseModel):
    """Doctor availability schedule"""
    day_of_week: str = Field(..., description="Monday, Tuesday, etc.")
    start_time: time
    end_time: time


class DoctorBase(BaseModel):
    """Base doctor model with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    specialization: str = Field(..., description="e.g., Cardiology, Neurology, General Practice")
    sub_specializations: Optional[List[str]] = []
    license_number: str
    license_state: str
    qualifications: Optional[List[Qualification]] = []
    years_of_experience: Optional[int] = Field(None, ge=0)
    primary_organization_id: Optional[str] = None
    organization_affiliations: Optional[List[OrganizationAffiliation]] = []
    consultation_fee: Optional[float] = Field(None, ge=0)
    availability: Optional[List[DoctorAvailability]] = []
    languages_spoken: Optional[List[str]] = ["English"]


class DoctorCreate(DoctorBase):
    """Model for creating a new doctor"""
    pass


class DoctorUpdate(BaseModel):
    """Model for updating a doctor (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    specialization: Optional[str] = None
    sub_specializations: Optional[List[str]] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    qualifications: Optional[List[Qualification]] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    primary_organization_id: Optional[str] = None
    organization_affiliations: Optional[List[OrganizationAffiliation]] = None
    consultation_fee: Optional[float] = Field(None, ge=0)
    availability: Optional[List[DoctorAvailability]] = None
    languages_spoken: Optional[List[str]] = None


class DoctorResponse(DoctorBase):
    """Model for doctor response (includes database fields)"""
    doctor_id: str
    rating: Optional[float] = Field(None, ge=0, le=5)
    total_patients_treated: Optional[int] = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "doctor_id": "650e8400-e29b-41d4-a716-446655440000",
                "first_name": "Dr. Sarah",
                "last_name": "Johnson",
                "email": "sarah.johnson@hospital.com",
                "phone": "+1234567890",
                "specialization": "Cardiology",
                "license_number": "MD123456",
                "license_state": "California",
                "years_of_experience": 15,
                "consultation_fee": 200.00,
                "rating": 4.8,
                "total_patients_treated": 1500,
                "is_active": True
            }
        }


class DoctorListResponse(BaseModel):
    """Model for paginated doctor list response"""
    doctors: List[DoctorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
