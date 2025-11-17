"""
Pydantic models for Health Vitals data
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MeasurementUnit(str, Enum):
    """Common measurement units"""
    CM = "cm"
    INCHES = "inches"
    KG = "kg"
    LBS = "lbs"
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    MMHG = "mmHg"
    MG_DL = "mg/dL"
    MMOL_L = "mmol/L"


class HealthStatus(str, Enum):
    """General health status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class DiabetesType(str, Enum):
    """Diabetes types"""
    TYPE_1 = "type_1"
    TYPE_2 = "type_2"
    GESTATIONAL = "gestational"
    PREDIABETES = "prediabetes"


class Height(BaseModel):
    """Height measurement"""
    value: float = Field(..., gt=0)
    unit: str = Field(default="cm", description="cm or inches")


class Weight(BaseModel):
    """Weight measurement"""
    value: float = Field(..., gt=0)
    unit: str = Field(default="kg", description="kg or lbs")


class Temperature(BaseModel):
    """Temperature measurement"""
    value: float = Field(..., gt=0)
    unit: str = Field(default="celsius", description="celsius or fahrenheit")


class BloodPressure(BaseModel):
    """Blood pressure reading"""
    systolic: int = Field(..., ge=50, le=300, description="Systolic pressure (mmHg)")
    diastolic: int = Field(..., ge=30, le=200, description="Diastolic pressure (mmHg)")
    arm: Optional[str] = Field(None, description="left or right")
    position: Optional[str] = Field(None, description="sitting, standing, lying")


class BloodGlucose(BaseModel):
    """Blood glucose measurement"""
    value: float = Field(..., gt=0)
    unit: str = Field(default="mg/dL", description="mg/dL or mmol/L")
    measurement_type: Optional[str] = Field(None, description="fasting, random, post_prandial")


class DiabetesStatus(BaseModel):
    """Diabetes status information"""
    has_diabetes: bool
    diabetes_type: Optional[DiabetesType] = None
    hba1c: Optional[float] = Field(None, ge=0, le=20, description="HbA1c percentage")
    on_medication: Optional[bool] = None


class Cholesterol(BaseModel):
    """Cholesterol levels"""
    total_cholesterol: Optional[float] = Field(None, ge=0, description="mg/dL")
    ldl: Optional[float] = Field(None, ge=0, description="LDL (bad cholesterol) in mg/dL")
    hdl: Optional[float] = Field(None, ge=0, description="HDL (good cholesterol) in mg/dL")
    triglycerides: Optional[float] = Field(None, ge=0, description="mg/dL")


class HealthVitalsBase(BaseModel):
    """Base health vitals model"""
    patient_id: str
    recorded_by: Optional[str] = Field(None, description="Doctor ID or nurse ID")
    visit_id: Optional[str] = None
    height: Optional[Height] = None
    weight: Optional[Weight] = None
    bmi: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[Temperature] = None
    blood_pressure: Optional[BloodPressure] = None
    heart_rate_bpm: Optional[int] = Field(None, ge=30, le=300, description="Heart rate in BPM")
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60, description="Breaths per minute")
    oxygen_saturation: Optional[float] = Field(None, ge=0, le=100, description="SpO2 percentage")
    blood_glucose: Optional[BloodGlucose] = None
    diabetes_status: Optional[DiabetesStatus] = None
    cholesterol: Optional[Cholesterol] = None
    general_health_status: Optional[HealthStatus] = None
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="Pain scale 0-10")
    notes: Optional[str] = None


class HealthVitalsCreate(HealthVitalsBase):
    """Model for creating new health vitals record"""
    pass


class HealthVitalsUpdate(BaseModel):
    """Model for updating health vitals (all fields optional)"""
    recorded_by: Optional[str] = None
    height: Optional[Height] = None
    weight: Optional[Weight] = None
    bmi: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[Temperature] = None
    blood_pressure: Optional[BloodPressure] = None
    heart_rate_bpm: Optional[int] = Field(None, ge=30, le=300)
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60)
    oxygen_saturation: Optional[float] = Field(None, ge=0, le=100)
    blood_glucose: Optional[BloodGlucose] = None
    diabetes_status: Optional[DiabetesStatus] = None
    cholesterol: Optional[Cholesterol] = None
    general_health_status: Optional[HealthStatus] = None
    pain_level: Optional[int] = Field(None, ge=0, le=10)
    notes: Optional[str] = None


class HealthVitalsResponse(HealthVitalsBase):
    """Model for health vitals response"""
    vital_id: str
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "vital_id": "750e8400-e29b-41d4-a716-446655440000",
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "recorded_at": "2024-01-15T14:30:00",
                "height": {"value": 175, "unit": "cm"},
                "weight": {"value": 70, "unit": "kg"},
                "bmi": 22.9,
                "blood_pressure": {"systolic": 120, "diastolic": 80},
                "heart_rate_bpm": 72,
                "oxygen_saturation": 98.0,
                "general_health_status": "good"
            }
        }


class HealthVitalsListResponse(BaseModel):
    """Model for paginated health vitals list"""
    vitals: List[HealthVitalsResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
