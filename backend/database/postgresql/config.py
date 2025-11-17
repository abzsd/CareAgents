"""
PostgreSQL Database Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(Path("../../.env"))

# Environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Table names
TABLES = {
    "patients": "patients",
    "doctors": "doctors",
    "organizations": "organizations",
    "prescriptions": "prescriptions",
    "health_vitals": "health_vitals",
    "medical_reports": "medical_reports",
    "users": "users"
}


def get_database_url() -> str:
    """
    Get PostgreSQL database URL.

    Returns:
        str: Database connection URL
    """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_table_name(table_key: str) -> str:
    """
    Get actual table name from configuration.

    Args:
        table_key: Key for the table

    Returns:
        str: Actual table name
    """
    if table_key not in TABLES:
        raise ValueError(f"Table {table_key} not found in configuration")

    return TABLES[table_key]
