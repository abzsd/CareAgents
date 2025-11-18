"""
Onboarding Service
Handles user onboarding and creates patient/doctor records
"""
from typing import Optional, Dict, Any
import asyncpg
import uuid
from datetime import date

from services.patient_service import PatientService
from services.doctor_service import DoctorService
from services.user_service import UserService
from models.patient import PatientCreate, Gender, BloodType
from models.doctor import DoctorCreate


class OnboardingService:
    """Service for handling user onboarding"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.patient_service = PatientService(pool)
        self.doctor_service = DoctorService(pool)
        self.user_service = UserService(pool)

    async def onboard_patient(
        self,
        user_id: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        gender: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        blood_type: Optional[str] = None,
        allergies: Optional[list] = None,
        chronic_conditions: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Onboard a patient user - creates patient record and links to user.

        Args:
            user_id: User ID from users table
            first_name: Patient's first name
            last_name: Patient's last name
            date_of_birth: Date of birth
            gender: Gender (Male, Female, Other, Prefer not to say)
            phone: Phone number
            email: Email address
            blood_type: Blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
            allergies: List of allergies
            chronic_conditions: List of chronic conditions
            **kwargs: Additional patient data (address, emergency_contact, insurance_info)

        Returns:
            Dictionary with patient record and updated user
        """
        # Validate gender
        try:
            gender_enum = Gender(gender)
        except ValueError:
            gender_enum = Gender.PREFER_NOT_TO_SAY

        # Validate blood type if provided
        blood_type_enum = None
        if blood_type:
            try:
                blood_type_enum = BloodType(blood_type)
            except ValueError:
                pass

        # Create patient data
        patient_data = PatientCreate(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender_enum,
            email=email,
            phone=phone,
            blood_type=blood_type_enum,
            allergies=allergies or [],
            chronic_conditions=chronic_conditions or [],
            address=kwargs.get('address'),
            emergency_contact=kwargs.get('emergency_contact'),
            insurance_info=kwargs.get('insurance_info')
        )

        # Create patient record
        patient = await self.patient_service.create_patient(patient_data, user_id=user_id)

        # Mark user as onboarded
        await self.user_service.mark_as_onboarded(user_id)

        return {
            "patient": patient,
            "message": "Patient onboarding successful"
        }

    async def onboard_doctor(
        self,
        user_id: str,
        first_name: str,
        last_name: str,
        specialization: str,
        license_number: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        experience_years: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Onboard a doctor user - creates doctor record and links to user.

        Args:
            user_id: User ID from users table
            first_name: Doctor's first name
            last_name: Doctor's last name
            specialization: Medical specialization
            license_number: Medical license number
            phone: Phone number
            email: Email address
            experience_years: Years of experience
            **kwargs: Additional doctor data (address, education, certifications)

        Returns:
            Dictionary with doctor record and updated user
        """
        # Create doctor data
        doctor_data = DoctorCreate(
            first_name=first_name,
            last_name=last_name,
            specialization=specialization,
            license_number=license_number,
            phone=phone,
            email=email,
            experience_years=experience_years,
            address=kwargs.get('address'),
            education=kwargs.get('education', []),
            certifications=kwargs.get('certifications', [])
        )

        # Create doctor record
        doctor = await self.doctor_service.create_doctor(doctor_data, user_id=user_id)

        # Mark user as onboarded
        await self.user_service.mark_as_onboarded(user_id)

        return {
            "doctor": doctor,
            "message": "Doctor onboarding successful"
        }

    async def check_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """
        Check if a user is onboarded and get their profile.

        Args:
            user_id: User ID

        Returns:
            Dictionary with onboarding status and profile data
        """
        # Get user
        user = await self.user_service.get_user(user_id)

        if not user:
            return {
                "is_onboarded": False,
                "user": None,
                "profile": None
            }

        # If user is onboarded, get their profile
        profile = None
        if user.is_onboarded:
            if user.role == "patient":
                profile = await self.patient_service.get_patient_by_user_id(user_id)
            elif user.role == "doctor":
                profile = await self.doctor_service.get_doctor_by_user_id(user_id)

        return {
            "is_onboarded": user.is_onboarded,
            "user": user,
            "profile": profile
        }
