"""
Admin Routes
Administrative endpoints for data fixes and maintenance
"""
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
import uuid
from datetime import datetime

from database.postgresql.connection import get_postgresql_pool


router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/fix-missing-profiles")
async def fix_missing_profiles(pool: asyncpg.Pool = Depends(get_postgresql_pool)):
    """
    Fix missing doctor/patient profiles for onboarded users.
    Creates profiles for users who are marked as onboarded but don't have corresponding records.

    Returns:
        Summary of fixes applied
    """
    async with pool.acquire() as conn:
        fixed_doctors = []
        fixed_patients = []

        try:
            # Fix missing doctor records
            missing_doctors_query = """
                SELECT u.user_id, u.email, u.display_name
                FROM users u
                LEFT JOIN doctors d ON u.user_id = d.user_id
                WHERE u.role = 'doctor'
                  AND u.is_onboarded = true
                  AND d.doctor_id IS NULL
            """

            missing_doctors = await conn.fetch(missing_doctors_query)

            for user in missing_doctors:
                user_id = user['user_id']
                email = user['email']
                display_name = user['display_name'] or "Doctor"

                # Split display name
                name_parts = display_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create doctor record
                doctor_insert = """
                    INSERT INTO doctors (
                        doctor_id, user_id, first_name, last_name,
                        specialization, license_number, email,
                        is_active, created_at, updated_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING doctor_id
                """

                doctor_id = await conn.fetchval(
                    doctor_insert,
                    user_id,  # Use same ID
                    user_id,
                    first_name,
                    last_name,
                    'General Practice',
                    f'MD{str(uuid.uuid4())[:6].upper()}',
                    email,
                    True,
                    datetime.utcnow(),
                    datetime.utcnow()
                )

                fixed_doctors.append({
                    "user_id": user_id,
                    "doctor_id": doctor_id,
                    "email": email,
                    "name": f"{first_name} {last_name}"
                })

            # Fix missing patient records
            missing_patients_query = """
                SELECT u.user_id, u.email, u.display_name
                FROM users u
                LEFT JOIN patients p ON u.user_id = p.user_id
                WHERE u.role = 'patient'
                  AND u.is_onboarded = true
                  AND p.patient_id IS NULL
            """

            missing_patients = await conn.fetch(missing_patients_query)

            for user in missing_patients:
                user_id = user['user_id']
                email = user['email']
                display_name = user['display_name'] or "Patient"

                # Split display name
                name_parts = display_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create patient record with minimal required data
                patient_insert = """
                    INSERT INTO patients (
                        patient_id, user_id, first_name, last_name,
                        date_of_birth, gender, email,
                        is_active, created_at, updated_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING patient_id
                """

                patient_id = await conn.fetchval(
                    patient_insert,
                    user_id,  # Use same ID
                    user_id,
                    first_name,
                    last_name,
                    datetime(1990, 1, 1).date(),  # Default DOB
                    'Prefer not to say',  # Default gender
                    email,
                    True,
                    datetime.utcnow(),
                    datetime.utcnow()
                )

                fixed_patients.append({
                    "user_id": user_id,
                    "patient_id": patient_id,
                    "email": email,
                    "name": f"{first_name} {last_name}"
                })

            return {
                "message": "Profile fixes completed",
                "doctors_fixed": len(fixed_doctors),
                "patients_fixed": len(fixed_patients),
                "details": {
                    "doctors": fixed_doctors,
                    "patients": fixed_patients
                }
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fix profiles: {str(e)}"
            )


@router.get("/check-orphaned-users")
async def check_orphaned_users(pool: asyncpg.Pool = Depends(get_postgresql_pool)):
    """
    Check for users who are marked as onboarded but don't have corresponding profiles.

    Returns:
        List of orphaned users
    """
    async with pool.acquire() as conn:
        try:
            # Check doctors
            orphaned_doctors_query = """
                SELECT u.user_id, u.email, u.display_name, u.role, u.is_onboarded
                FROM users u
                LEFT JOIN doctors d ON u.user_id = d.user_id
                WHERE u.role = 'doctor'
                  AND u.is_onboarded = true
                  AND d.doctor_id IS NULL
            """

            orphaned_doctors = await conn.fetch(orphaned_doctors_query)

            # Check patients
            orphaned_patients_query = """
                SELECT u.user_id, u.email, u.display_name, u.role, u.is_onboarded
                FROM users u
                LEFT JOIN patients p ON u.user_id = p.user_id
                WHERE u.role = 'patient'
                  AND u.is_onboarded = true
                  AND p.patient_id IS NULL
            """

            orphaned_patients = await conn.fetch(orphaned_patients_query)

            return {
                "orphaned_doctors": [dict(row) for row in orphaned_doctors],
                "orphaned_patients": [dict(row) for row in orphaned_patients],
                "total_issues": len(orphaned_doctors) + len(orphaned_patients)
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check orphaned users: {str(e)}"
            )
