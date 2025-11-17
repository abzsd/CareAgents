"""
PostgreSQL query tools for AI agents
"""
import asyncpg
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    """PostgreSQL configuration"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="careagents")
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")


class PostgresToolkit:
    """PostgreSQL toolkit for agents"""

    def __init__(self, config: PostgresConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=2,
                max_size=10,
            )
        return self.pool

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None


# Global toolkit instance
_toolkit: Optional[PostgresToolkit] = None


def init_postgres_toolkit(config: PostgresConfig):
    """Initialize PostgreSQL toolkit"""
    global _toolkit
    _toolkit = PostgresToolkit(config)
    return _toolkit


def get_postgres_toolkit() -> PostgresToolkit:
    """Get PostgreSQL toolkit instance"""
    global _toolkit
    if _toolkit is None:
        raise RuntimeError("PostgresToolkit not initialized. Call init_postgres_toolkit first.")
    return _toolkit


async def query_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """
    Query patient information by patient ID

    Args:
        patient_id: The patient's unique identifier

    Returns:
        Patient information as a dictionary
    """
    toolkit = get_postgres_toolkit()
    pool = await toolkit.get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                patient_id, first_name, last_name, date_of_birth, age, gender,
                email, phone, address, emergency_contact, blood_type, allergies,
                chronic_conditions, insurance_info, is_active, created_at, updated_at
            FROM patients
            WHERE patient_id = $1 AND is_active = TRUE
            """,
            patient_id
        )

        if not row:
            return {"error": f"Patient with ID {patient_id} not found"}

        return dict(row)


async def query_patient_records(patient_id: str, limit: int = 100) -> Dict[str, Any]:
    """
    Query all medical records for a patient including vitals, prescriptions, and reports

    Args:
        patient_id: The patient's unique identifier
        limit: Maximum number of records to return per category

    Returns:
        Comprehensive patient records
    """
    toolkit = get_postgres_toolkit()
    pool = await toolkit.get_pool()

    async with pool.acquire() as conn:
        # Get patient info
        patient = await conn.fetchrow(
            """
            SELECT
                patient_id, first_name, last_name, date_of_birth, age, gender,
                email, phone, blood_type, allergies, chronic_conditions
            FROM patients
            WHERE patient_id = $1 AND is_active = TRUE
            """,
            patient_id
        )

        if not patient:
            return {"error": f"Patient with ID {patient_id} not found"}

        # Get health vitals
        vitals = await conn.fetch(
            """
            SELECT
                vital_id, vital_type, value, unit, recorded_at, notes
            FROM health_vitals
            WHERE patient_id = $1 AND is_active = TRUE
            ORDER BY recorded_at DESC
            LIMIT $2
            """,
            patient_id, limit
        )

        # Get prescriptions
        prescriptions = await conn.fetch(
            """
            SELECT
                p.prescription_id, p.medications, p.diagnosis, p.notes,
                p.prescribed_date, p.valid_until,
                d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                d.specialization
            FROM prescriptions p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            WHERE p.patient_id = $1 AND p.is_active = TRUE
            ORDER BY p.prescribed_date DESC
            LIMIT $2
            """,
            patient_id, limit
        )

        # Get medical reports
        reports = await conn.fetch(
            """
            SELECT
                mr.report_id, mr.report_type, mr.title, mr.content,
                mr.file_url, mr.report_date,
                d.first_name as doctor_first_name, d.last_name as doctor_last_name
            FROM medical_reports mr
            LEFT JOIN doctors d ON mr.doctor_id = d.doctor_id
            WHERE mr.patient_id = $1 AND mr.is_active = TRUE
            ORDER BY mr.report_date DESC
            LIMIT $2
            """,
            patient_id, limit
        )

        return {
            "patient": dict(patient),
            "vitals": [dict(v) for v in vitals],
            "prescriptions": [dict(p) for p in prescriptions],
            "reports": [dict(r) for r in reports],
        }


async def query_health_vitals(
    patient_id: str,
    vital_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Query health vitals for a patient with optional filters

    Args:
        patient_id: The patient's unique identifier
        vital_type: Optional filter by vital type (e.g., 'blood_pressure', 'temperature')
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)
        limit: Maximum number of records to return

    Returns:
        List of health vital records
    """
    toolkit = get_postgres_toolkit()
    pool = await toolkit.get_pool()

    query = """
        SELECT
            vital_id, vital_type, value, unit, recorded_at, notes,
            recorded_by, created_at
        FROM health_vitals
        WHERE patient_id = $1 AND is_active = TRUE
    """
    params = [patient_id]
    param_count = 1

    if vital_type:
        param_count += 1
        query += f" AND vital_type = ${param_count}"
        params.append(vital_type)

    if start_date:
        param_count += 1
        query += f" AND recorded_at >= ${param_count}"
        params.append(start_date)

    if end_date:
        param_count += 1
        query += f" AND recorded_at <= ${param_count}"
        params.append(end_date)

    query += f" ORDER BY recorded_at DESC LIMIT ${param_count + 1}"
    params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def query_prescriptions(
    patient_id: str,
    active_only: bool = True,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query prescriptions for a patient

    Args:
        patient_id: The patient's unique identifier
        active_only: Whether to return only active prescriptions
        limit: Maximum number of records to return

    Returns:
        List of prescription records
    """
    toolkit = get_postgres_toolkit()
    pool = await toolkit.get_pool()

    query = """
        SELECT
            p.prescription_id, p.medications, p.diagnosis, p.notes,
            p.prescribed_date, p.valid_until, p.is_active,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            d.specialization, d.license_number
        FROM prescriptions p
        LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
        WHERE p.patient_id = $1
    """
    params = [patient_id]

    if active_only:
        query += " AND p.is_active = TRUE AND (p.valid_until IS NULL OR p.valid_until >= CURRENT_DATE)"

    query += " ORDER BY p.prescribed_date DESC LIMIT $2"
    params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def query_medical_reports(
    patient_id: str,
    report_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Query medical reports for a patient

    Args:
        patient_id: The patient's unique identifier
        report_type: Optional filter by report type
        limit: Maximum number of records to return

    Returns:
        List of medical report records
    """
    toolkit = get_postgres_toolkit()
    pool = await toolkit.get_pool()

    query = """
        SELECT
            mr.report_id, mr.report_type, mr.title, mr.content,
            mr.file_url, mr.report_date,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            d.specialization
        FROM medical_reports mr
        LEFT JOIN doctors d ON mr.doctor_id = d.doctor_id
        WHERE mr.patient_id = $1 AND mr.is_active = TRUE
    """
    params = [patient_id]

    if report_type:
        query += " AND mr.report_type = $2"
        params.append(report_type)
        query += " ORDER BY mr.report_date DESC LIMIT $3"
        params.append(limit)
    else:
        query += " ORDER BY mr.report_date DESC LIMIT $2"
        params.append(limit)

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


# Tool definitions for Anthropic Claude
TOOLS = [
    {
        "name": "query_patient_by_id",
        "description": "Retrieve detailed patient information by patient ID. Returns patient demographics, contact info, medical conditions, allergies, and insurance information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "query_patient_records",
        "description": "Retrieve comprehensive medical records for a patient including health vitals, prescriptions, and medical reports. This is the most complete view of a patient's medical history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return per category",
                    "default": 100
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "query_health_vitals",
        "description": "Query health vital signs for a patient with optional filters by vital type and date range. Useful for tracking specific metrics over time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "vital_type": {
                    "type": "string",
                    "description": "Type of vital to filter (e.g., 'blood_pressure', 'temperature', 'heart_rate')"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date for filtering in ISO format (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date for filtering in ISO format (YYYY-MM-DD)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return",
                    "default": 100
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "query_prescriptions",
        "description": "Query prescription records for a patient. Can filter for active prescriptions only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "active_only": {
                    "type": "boolean",
                    "description": "Whether to return only active and valid prescriptions",
                    "default": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return",
                    "default": 50
                }
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "query_medical_reports",
        "description": "Query medical reports for a patient with optional filtering by report type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "The unique identifier for the patient"
                },
                "report_type": {
                    "type": "string",
                    "description": "Type of medical report to filter (e.g., 'lab_result', 'imaging', 'consultation')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to return",
                    "default": 50
                }
            },
            "required": ["patient_id"]
        }
    }
]
