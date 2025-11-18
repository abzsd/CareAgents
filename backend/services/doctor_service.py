"""
Service layer for Doctor operations
"""
from typing import List, Optional, Dict, Any
import asyncpg
import uuid

from database.postgresql.repository import BaseRepository
from models.doctor import DoctorCreate, DoctorUpdate, DoctorResponse


class DoctorService:
    """Service for managing doctors"""

    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize doctor service.

        Args:
            pool: PostgreSQL connection pool
        """
        self.repository = BaseRepository(pool, "doctors")

    async def create_doctor(self, doctor_data: DoctorCreate) -> DoctorResponse:
        """
        Create a new doctor.

        Args:
            doctor_data: Doctor data

        Returns:
            Created doctor record
        """
        # Generate UUID for doctor_id
        doctor_id = str(uuid.uuid4())

        # Convert Pydantic model to dict
        data = doctor_data.model_dump()
        data['doctor_id'] = doctor_id
        data['is_active'] = True
        data['rating'] = 0.0
        data['total_patients_treated'] = 0

        # Insert the record
        result = await self.repository.insert(data)

        return DoctorResponse(**result)

    async def get_doctor(self, doctor_id: str) -> Optional[DoctorResponse]:
        """
        Get a doctor by ID.

        Args:
            doctor_id: Doctor ID

        Returns:
            Doctor record or None if not found
        """
        result = await self.repository.find_by_id("doctor_id", doctor_id)

        if result:
            return DoctorResponse(**result)
        return None

    async def get_doctor_by_user_id(self, user_id: str) -> Optional[DoctorResponse]:
        """
        Get doctor by user ID.

        Args:
            user_id: User ID

        Returns:
            Doctor record or None if not found
        """
        results = await self.repository.find_by_filter({"user_id": user_id}, limit=1)

        if results:
            return DoctorResponse(**results[0])
        return None

    async def list_doctors(
        self,
        page: int = 1,
        page_size: int = 20,
        specialization: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        List doctors with pagination and optional filters.

        Args:
            page: Page number
            page_size: Number of records per page
            specialization: Filter by specialization
            active_only: Only return active doctors

        Returns:
            Dictionary containing doctors and pagination info
        """
        offset = (page - 1) * page_size

        # Build query based on filters
        conditions = []
        params = []
        param_count = 0

        if active_only:
            param_count += 1
            conditions.append(f"is_active = ${param_count}")
            params.append(True)

        if specialization:
            param_count += 1
            conditions.append(f"specialization = ${param_count}")
            params.append(specialization)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count

        query = f"""
            SELECT * FROM doctors
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        params.extend([page_size, offset])

        records = await self.repository.execute_custom_query(query, *params)

        # Count query
        count_query = f"""
            SELECT COUNT(*) as count FROM doctors
            WHERE {where_clause}
        """
        count_result = await self.repository.execute_custom_query(count_query, *params[:param_count-2])

        total = count_result[0]['count'] if count_result else 0
        total_pages = (total + page_size - 1) // page_size

        return {
            "doctors": [DoctorResponse(**record) for record in records],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def search_doctors(
        self,
        search_term: str,
        limit: int = 20
    ) -> List[DoctorResponse]:
        """
        Search doctors by name, specialization, or email.

        Args:
            search_term: Search term
            limit: Maximum number of results

        Returns:
            List of matching doctors
        """
        search_fields = ["first_name", "last_name", "specialization", "email"]
        results = await self.repository.search(search_fields, search_term, limit)

        return [DoctorResponse(**record) for record in results]

    async def update_doctor(
        self,
        doctor_id: str,
        update_data: DoctorUpdate
    ) -> Optional[DoctorResponse]:
        """
        Update a doctor.

        Args:
            doctor_id: Doctor ID
            update_data: Updated doctor data

        Returns:
            Updated doctor record or None if not found
        """
        # Convert Pydantic model to dict, excluding unset fields
        data = update_data.model_dump(exclude_unset=True)

        # Update the record
        success = await self.repository.update("doctor_id", doctor_id, data)

        if success:
            return await self.get_doctor(doctor_id)
        return None

    async def delete_doctor(self, doctor_id: str) -> bool:
        """
        Soft delete a doctor.

        Args:
            doctor_id: Doctor ID

        Returns:
            True if deletion was successful
        """
        return await self.repository.soft_delete("doctor_id", doctor_id)

    async def get_specializations(self) -> List[str]:
        """
        Get list of all unique specializations.

        Returns:
            List of specializations
        """
        query = """
            SELECT DISTINCT specialization FROM doctors
            WHERE is_active = true AND specialization IS NOT NULL
            ORDER BY specialization
        """
        results = await self.repository.execute_custom_query(query)

        return [record['specialization'] for record in results]
