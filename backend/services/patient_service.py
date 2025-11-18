"""
Patient Service Layer for PostgreSQL
Handles business logic for patient operations
"""
from typing import List, Optional, Dict, Any
import asyncpg
from database.postgresql.repository import BaseRepository
from models.patient import PatientCreate, PatientUpdate, PatientResponse
from datetime import datetime, date
import uuid


class PatientRepository(BaseRepository):
    """Repository for patient operations"""

    def __init__(self, pool: asyncpg.Pool):
        super().__init__(pool, "patients")

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find patient by email"""
        results = await self.find_by_filter({"email": email}, limit=1)
        return results[0] if results else None

    async def search_patients(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search patients by name, email, or phone.

        Args:
            search_term: Search term
            limit: Maximum results

        Returns:
            List of matching patients
        """
        search_fields = ["first_name", "last_name", "email", "phone"]
        return await self.search(search_fields, search_term, limit)


class PatientService:
    """Service class for patient operations"""

    def __init__(self, pool: asyncpg.Pool):
        self.repository = PatientRepository(pool)

    async def create_patient(self, patient_data: PatientCreate, user_id: Optional[str] = None) -> PatientResponse:
        """
        Create a new patient.

        Args:
            patient_data: Patient creation data
            user_id: Optional user ID to link patient to a user account

        Returns:
            Created patient response
        """
        # Generate patient ID
        patient_dict = patient_data.model_dump(exclude_none=True)
        patient_dict['patient_id'] = str(uuid.uuid4())

        # Link to user if provided
        if user_id:
            patient_dict['user_id'] = user_id

        # Calculate age from date of birth
        if patient_data.date_of_birth:
            today = date.today()
            age = today.year - patient_data.date_of_birth.year
            if today.month < patient_data.date_of_birth.month or \
               (today.month == patient_data.date_of_birth.month and today.day < patient_data.date_of_birth.day):
                age -= 1
            patient_dict['age'] = age

        patient_dict['is_active'] = True

        # Convert date_of_birth - keep as date object for PostgreSQL
        # asyncpg handles date objects directly, no need to convert to string

        # Convert enum values to strings
        if 'gender' in patient_dict:
            patient_dict['gender'] = patient_dict['gender'].value if hasattr(patient_dict['gender'], 'value') else patient_dict['gender']

        if 'blood_type' in patient_dict:
            patient_dict['blood_type'] = patient_dict['blood_type'].value if hasattr(patient_dict['blood_type'], 'value') else patient_dict['blood_type']

        # Convert nested Pydantic models to dicts
        if 'address' in patient_dict and hasattr(patient_dict['address'], 'model_dump'):
            patient_dict['address'] = patient_dict['address'].model_dump()

        if 'emergency_contact' in patient_dict and hasattr(patient_dict['emergency_contact'], 'model_dump'):
            patient_dict['emergency_contact'] = patient_dict['emergency_contact'].model_dump()

        if 'insurance_info' in patient_dict and hasattr(patient_dict['insurance_info'], 'model_dump'):
            patient_dict['insurance_info'] = patient_dict['insurance_info'].model_dump()

        # Insert into database
        created = await self.repository.insert(patient_dict)

        return PatientResponse(**created)

    async def get_patient(self, patient_id: str) -> Optional[PatientResponse]:
        """
        Get patient by ID.

        Args:
            patient_id: Patient ID

        Returns:
            Patient response or None
        """
        patient = await self.repository.find_by_id("patient_id", patient_id)
        return PatientResponse(**patient) if patient else None

    async def get_patient_by_user_id(self, user_id: str) -> Optional[PatientResponse]:
        """
        Get patient by user ID.

        Args:
            user_id: User ID

        Returns:
            Patient response or None
        """
        results = await self.repository.find_by_filter({"user_id": user_id, "is_active": True}, limit=1)
        return PatientResponse(**results[0]) if results else None

    async def update_patient(self, patient_id: str, patient_data: PatientUpdate) -> Optional[PatientResponse]:
        """
        Update patient information.

        Args:
            patient_id: Patient ID
            patient_data: Updated patient data

        Returns:
            Updated patient response or None
        """
        # Get current patient
        existing = await self.repository.find_by_id("patient_id", patient_id)
        if not existing:
            return None

        # Prepare update data
        update_dict = patient_data.model_dump(exclude_none=True)

        # Recalculate age if date of birth is updated
        # Keep date_of_birth as date object for PostgreSQL
        if 'date_of_birth' in update_dict:
            dob = patient_data.date_of_birth
            today = date.today()
            age = today.year - dob.year
            if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                age -= 1
            update_dict['age'] = age

        # Convert enum values to strings
        if 'gender' in update_dict:
            update_dict['gender'] = update_dict['gender'].value if hasattr(update_dict['gender'], 'value') else update_dict['gender']

        if 'blood_type' in update_dict:
            update_dict['blood_type'] = update_dict['blood_type'].value if hasattr(update_dict['blood_type'], 'value') else update_dict['blood_type']

        # Convert nested Pydantic models to dicts
        if 'address' in update_dict and hasattr(update_dict['address'], 'model_dump'):
            update_dict['address'] = update_dict['address'].model_dump()

        if 'emergency_contact' in update_dict and hasattr(update_dict['emergency_contact'], 'model_dump'):
            update_dict['emergency_contact'] = update_dict['emergency_contact'].model_dump()

        if 'insurance_info' in update_dict and hasattr(update_dict['insurance_info'], 'model_dump'):
            update_dict['insurance_info'] = update_dict['insurance_info'].model_dump()

        # Update in database
        await self.repository.update("patient_id", patient_id, update_dict)

        # Return updated patient
        return await self.get_patient(patient_id)

    async def delete_patient(self, patient_id: str) -> bool:
        """
        Soft delete a patient.

        Args:
            patient_id: Patient ID

        Returns:
            True if successful
        """
        return await self.repository.soft_delete("patient_id", patient_id)

    async def list_patients(self, page: int = 1, page_size: int = 20, active_only: bool = True) -> Dict[str, Any]:
        """
        List patients with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            active_only: Only return active patients

        Returns:
            Dictionary with patients and pagination info
        """
        offset = (page - 1) * page_size

        if active_only:
            patients = await self.repository.find_by_filter({"is_active": True}, limit=page_size)
            total = await self.repository.count({"is_active": True})
        else:
            patients = await self.repository.find_all(limit=page_size, offset=offset)
            total = await self.repository.count()

        total_pages = (total + page_size - 1) // page_size

        return {
            "patients": [PatientResponse(**p) for p in patients],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def search_patients(self, search_term: str, limit: int = 20) -> List[PatientResponse]:
        """
        Search patients.

        Args:
            search_term: Search term
            limit: Maximum results

        Returns:
            List of matching patients
        """
        patients = await self.repository.search_patients(search_term, limit)
        return [PatientResponse(**p) for p in patients]
