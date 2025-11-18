"""
Service layer for Appointment operations
"""
from typing import List, Optional, Dict, Any
import asyncpg
import uuid
from datetime import datetime, date

from database.postgresql.repository import BaseRepository
from models.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentStatus
)


class AppointmentService:
    """Service for managing appointments"""

    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize appointment service.

        Args:
            pool: PostgreSQL connection pool
        """
        self.repository = BaseRepository(pool, "appointments")

    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentResponse:
        """
        Create a new appointment.

        Args:
            appointment_data: Appointment data

        Returns:
            Created appointment record
        """
        # Generate UUID for appointment_id
        appointment_id = str(uuid.uuid4())

        # Convert Pydantic model to dict
        data = appointment_data.model_dump()
        data['appointment_id'] = appointment_id
        data['status'] = AppointmentStatus.SCHEDULED.value

        # Convert enums to strings
        if 'appointment_type' in data:
            data['appointment_type'] = data['appointment_type'].value if hasattr(data['appointment_type'], 'value') else data['appointment_type']

        # Insert the record
        result = await self.repository.insert(data)

        # Enrich with patient and doctor names
        enriched = await self._enrich_appointment(result)

        return AppointmentResponse(**enriched)

    async def get_appointment(self, appointment_id: str) -> Optional[AppointmentResponse]:
        """
        Get an appointment by ID.

        Args:
            appointment_id: Appointment ID

        Returns:
            Appointment record or None if not found
        """
        result = await self.repository.find_by_id("appointment_id", appointment_id)

        if result:
            enriched = await self._enrich_appointment(result)
            return AppointmentResponse(**enriched)
        return None

    async def get_patient_appointments(
        self,
        patient_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all appointments for a patient.

        Args:
            patient_id: Patient ID
            page: Page number
            page_size: Number of records per page
            status: Filter by status (optional)

        Returns:
            Dictionary containing appointments and pagination info
        """
        offset = (page - 1) * page_size

        # Build query based on status filter
        if status:
            query = """
                SELECT * FROM appointments
                WHERE patient_id = $1 AND status = $2 AND is_active = true
                ORDER BY appointment_date DESC, appointment_time DESC
                LIMIT $3 OFFSET $4
            """
            records = await self.repository.execute_custom_query(query, patient_id, status, page_size, offset)

            count_query = """
                SELECT COUNT(*) as count FROM appointments
                WHERE patient_id = $1 AND status = $2 AND is_active = true
            """
            count_result = await self.repository.execute_custom_query(count_query, patient_id, status)
        else:
            query = """
                SELECT * FROM appointments
                WHERE patient_id = $1 AND is_active = true
                ORDER BY appointment_date DESC, appointment_time DESC
                LIMIT $2 OFFSET $3
            """
            records = await self.repository.execute_custom_query(query, patient_id, page_size, offset)

            count_query = """
                SELECT COUNT(*) as count FROM appointments
                WHERE patient_id = $1 AND is_active = true
            """
            count_result = await self.repository.execute_custom_query(count_query, patient_id)

        total = count_result[0]['count'] if count_result else 0
        total_pages = (total + page_size - 1) // page_size

        # Enrich appointments with names
        enriched_records = []
        for record in records:
            enriched = await self._enrich_appointment(record)
            enriched_records.append(AppointmentResponse(**enriched))

        return {
            "appointments": enriched_records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def get_doctor_appointments(
        self,
        doctor_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        appointment_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get all appointments for a doctor.

        Args:
            doctor_id: Doctor ID
            page: Page number
            page_size: Number of records per page
            status: Filter by status (optional)
            appointment_date: Filter by date (optional)

        Returns:
            Dictionary containing appointments and pagination info
        """
        offset = (page - 1) * page_size

        # Build query based on filters
        conditions = ["doctor_id = $1", "is_active = true"]
        params = [doctor_id]
        param_count = 1

        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)

        if appointment_date:
            param_count += 1
            conditions.append(f"appointment_date = ${param_count}")
            params.append(appointment_date)

        where_clause = " AND ".join(conditions)

        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count

        query = f"""
            SELECT * FROM appointments
            WHERE {where_clause}
            ORDER BY appointment_date ASC, appointment_time ASC
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        params.extend([page_size, offset])

        records = await self.repository.execute_custom_query(query, *params)

        # Count query
        count_query = f"""
            SELECT COUNT(*) as count FROM appointments
            WHERE {where_clause}
        """
        count_result = await self.repository.execute_custom_query(count_query, *params[:param_count-2])

        total = count_result[0]['count'] if count_result else 0
        total_pages = (total + page_size - 1) // page_size

        # Enrich appointments with names
        enriched_records = []
        for record in records:
            enriched = await self._enrich_appointment(record)
            enriched_records.append(AppointmentResponse(**enriched))

        return {
            "appointments": enriched_records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    async def update_appointment(
        self,
        appointment_id: str,
        update_data: AppointmentUpdate
    ) -> Optional[AppointmentResponse]:
        """
        Update an appointment.

        Args:
            appointment_id: Appointment ID
            update_data: Updated appointment data

        Returns:
            Updated appointment record or None if not found
        """
        # Convert Pydantic model to dict, excluding unset fields
        data = update_data.model_dump(exclude_unset=True)

        # Convert enums to strings
        if 'appointment_type' in data and data['appointment_type']:
            data['appointment_type'] = data['appointment_type'].value if hasattr(data['appointment_type'], 'value') else data['appointment_type']

        if 'status' in data and data['status']:
            data['status'] = data['status'].value if hasattr(data['status'], 'value') else data['status']

        # Update the record
        success = await self.repository.update("appointment_id", appointment_id, data)

        if success:
            return await self.get_appointment(appointment_id)
        return None

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Cancel an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            True if cancellation was successful
        """
        return await self.repository.update(
            "appointment_id",
            appointment_id,
            {"status": AppointmentStatus.CANCELLED.value}
        )

    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        Soft delete an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            True if deletion was successful
        """
        return await self.repository.soft_delete("appointment_id", appointment_id)

    async def _enrich_appointment(self, appointment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich appointment with patient and doctor names.

        Args:
            appointment: Appointment record

        Returns:
            Enriched appointment record
        """
        # Get patient name
        patient_query = """
            SELECT first_name, last_name FROM patients WHERE patient_id = $1
        """
        patient_result = await self.repository.execute_custom_query(
            patient_query,
            appointment['patient_id']
        )

        if patient_result:
            patient = patient_result[0]
            appointment['patient_name'] = f"{patient['first_name']} {patient['last_name']}"

        # Get doctor name and specialization
        doctor_query = """
            SELECT first_name, last_name, specialization FROM doctors WHERE doctor_id = $1
        """
        doctor_result = await self.repository.execute_custom_query(
            doctor_query,
            appointment['doctor_id']
        )

        if doctor_result:
            doctor = doctor_result[0]
            appointment['doctor_name'] = f"Dr. {doctor['first_name']} {doctor['last_name']}"
            appointment['doctor_specialization'] = doctor['specialization']

        return appointment

    async def get_upcoming_appointments_count(self, patient_id: str) -> int:
        """Get count of upcoming appointments for a patient."""
        query = """
            SELECT COUNT(*) as count FROM appointments
            WHERE patient_id = $1
            AND status IN ('scheduled', 'confirmed')
            AND appointment_date >= CURRENT_DATE
            AND is_active = true
        """
        result = await self.repository.execute_custom_query(query, patient_id)
        return result[0]['count'] if result else 0

    async def get_todays_appointments_count(self, doctor_id: str) -> int:
        """Get count of today's appointments for a doctor."""
        query = """
            SELECT COUNT(*) as count FROM appointments
            WHERE doctor_id = $1
            AND appointment_date = CURRENT_DATE
            AND status IN ('scheduled', 'confirmed', 'in_progress')
            AND is_active = true
        """
        result = await self.repository.execute_custom_query(query, doctor_id)
        return result[0]['count'] if result else 0
