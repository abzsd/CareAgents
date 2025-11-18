"""
Service layer for Medical History operations
"""
from typing import List, Optional, Dict, Any
import asyncpg
import uuid

from database.postgresql.repository import BaseRepository
from models.medical_history import (
    MedicalHistoryCreate,
    MedicalHistoryUpdate,
    MedicalHistoryResponse
)


class MedicalHistoryService:
    """Service for managing medical history records"""

    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize medical history service.

        Args:
            pool: PostgreSQL connection pool
        """
        self.repository = BaseRepository(pool, "medical_history")

    async def create_medical_history(self, history_data: MedicalHistoryCreate) -> MedicalHistoryResponse:
        """
        Create a new medical history record.

        Args:
            history_data: Medical history data

        Returns:
            Created medical history record
        """
        # Generate UUID for history_id
        history_id = str(uuid.uuid4())

        # Convert Pydantic model to dict
        data = history_data.model_dump()
        data['history_id'] = history_id

        # Convert prescriptions list to proper format
        if data.get('prescriptions'):
            data['prescriptions'] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in data['prescriptions']]

        # Insert the record
        result = await self.repository.insert(data)

        return MedicalHistoryResponse(**result)

    async def get_medical_history(self, history_id: str) -> Optional[MedicalHistoryResponse]:
        """
        Get a medical history record by ID.

        Args:
            history_id: Medical history ID

        Returns:
            Medical history record or None if not found
        """
        result = await self.repository.find_by_id("history_id", history_id)

        if result:
            return MedicalHistoryResponse(**result)
        return None

    async def get_patient_medical_history(
        self,
        patient_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get all medical history records for a patient with pagination.

        Args:
            patient_id: Patient ID
            page: Page number
            page_size: Number of records per page

        Returns:
            Dictionary containing records, total count, and pagination info
        """
        offset = (page - 1) * page_size

        # Get records for the patient, ordered by visit_date descending
        query = """
            SELECT * FROM medical_history
            WHERE patient_id = $1 AND is_active = true
            ORDER BY visit_date DESC, created_at DESC
            LIMIT $2 OFFSET $3
        """

        records = await self.repository.execute_custom_query(query, patient_id, page_size, offset)

        # Get total count
        total = await self.repository.count({"patient_id": patient_id, "is_active": True})

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        return {
            "records": [MedicalHistoryResponse(**record) for record in records],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def get_doctor_patients_with_history(
        self,
        doctor_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get all patients who have medical history with this doctor.

        Args:
            doctor_id: Doctor ID
            page: Page number
            page_size: Number of records per page

        Returns:
            Dictionary containing patient records with their latest medical history
        """
        offset = (page - 1) * page_size

        # Get distinct patients with their latest medical history record
        query = """
            SELECT DISTINCT ON (p.patient_id)
                p.*,
                mh.history_id,
                mh.visit_date,
                mh.diagnosis,
                mh.health_status,
                mh.blood_pressure
            FROM patients p
            INNER JOIN medical_history mh ON p.patient_id = mh.patient_id
            WHERE mh.doctor_id = $1 AND p.is_active = true AND mh.is_active = true
            ORDER BY p.patient_id, mh.visit_date DESC
            LIMIT $2 OFFSET $3
        """

        records = await self.repository.execute_custom_query(query, doctor_id, page_size, offset)

        # Get total count of distinct patients
        count_query = """
            SELECT COUNT(DISTINCT p.patient_id) as count
            FROM patients p
            INNER JOIN medical_history mh ON p.patient_id = mh.patient_id
            WHERE mh.doctor_id = $1 AND p.is_active = true AND mh.is_active = true
        """
        count_result = await self.repository.execute_custom_query(count_query, doctor_id)
        total = count_result[0]['count'] if count_result else 0

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        return {
            "patients": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def get_all_patients(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get all patients in the system.

        Args:
            page: Page number
            page_size: Number of records per page

        Returns:
            Dictionary containing patient records and pagination info
        """
        offset = (page - 1) * page_size

        # Get all patients with optional user info
        query = """
            SELECT
                p.patient_id,
                p.user_id,
                p.first_name,
                p.last_name,
                p.email,
                p.phone,
                p.date_of_birth,
                p.age,
                p.gender,
                p.blood_type,
                p.is_active,
                p.created_at,
                p.updated_at,
                u.display_name,
                u.photo_url
            FROM patients p
            LEFT JOIN users u ON p.user_id = u.user_id
            WHERE p.is_active = true
            ORDER BY p.created_at DESC
            LIMIT $1 OFFSET $2
        """

        records = await self.repository.execute_custom_query(query, page_size, offset)

        # Get total count
        count_query = "SELECT COUNT(*) as count FROM patients WHERE is_active = true"
        count_result = await self.repository.execute_custom_query(count_query)
        total = count_result[0]['count'] if count_result else 0

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        return {
            "patients": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def update_medical_history(
        self,
        history_id: str,
        update_data: MedicalHistoryUpdate
    ) -> Optional[MedicalHistoryResponse]:
        """
        Update a medical history record.

        Args:
            history_id: Medical history ID
            update_data: Updated medical history data

        Returns:
            Updated medical history record or None if not found
        """
        # Convert Pydantic model to dict, excluding unset fields
        data = update_data.model_dump(exclude_unset=True)

        # Convert prescriptions if present
        if 'prescriptions' in data and data['prescriptions']:
            data['prescriptions'] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in data['prescriptions']]

        # Update the record
        success = await self.repository.update("history_id", history_id, data)

        if success:
            return await self.get_medical_history(history_id)
        return None

    async def delete_medical_history(self, history_id: str) -> bool:
        """
        Soft delete a medical history record.

        Args:
            history_id: Medical history ID

        Returns:
            True if deletion was successful
        """
        return await self.repository.soft_delete("history_id", history_id)
