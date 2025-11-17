"""
Pydantic models for Patient data
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class Gender(str, Enum):
    """Gender enum"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class BloodType(str, Enum):
    """Blood type enum"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class Address(BaseModel):
    """Address model"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class EmergencyContact(BaseModel):
    """Emergency contact model"""
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None


class InsuranceInfo(BaseModel):
    """Insurance information model"""
    provider: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None


class PatientBase(BaseModel):
    """Base patient model with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Gender
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Address] = None
    emergency_contact: Optional[EmergencyContact] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []
    insurance_info: Optional[InsuranceInfo] = None


class PatientCreate(PatientBase):
    """Model for creating a new patient"""
    pass


class PatientUpdate(BaseModel):
    """Model for updating a patient (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Address] = None
    emergency_contact: Optional[EmergencyContact] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    insurance_info: Optional[InsuranceInfo] = None


class PatientResponse(PatientBase):
    """Model for patient response (includes database fields)"""
    patient_id: str
    age: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-15",
                "age": 34,
                "gender": "Male",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "blood_type": "A+",
                "is_active": True,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            }
        }


class PatientListResponse(BaseModel):
    """Model for paginated patient list response"""
    patients: List[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
