"""
PostgreSQL connection manager for FastAPI.
Implements connection pooling and session management.
"""
from typing import Optional, Generator
from contextlib import contextmanager
import asyncpg
import asyncio
from functools import lru_cache
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables from .env file
load_dotenv(Path(".env"))


class PostgreSQLConnection:
    """
    PostgreSQL connection manager for FastAPI.
    Implements connection pooling for better performance.
    """

    _instance: Optional['PostgreSQLConnection'] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize PostgreSQL connection parameters"""
        if self._pool is None:
            self.host = os.getenv("DB_HOST", "localhost")
            self.port = int(os.getenv("DB_PORT", "5432"))
            self.database = os.getenv("DB_NAME", "healthcare_db")
            self.user = os.getenv("DB_USER", "postgres")
            self.password = os.getenv("DB_PASSWORD", "postgres")
            self.min_size = int(os.getenv("DB_POOL_MIN_SIZE", "10"))
            self.max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))

    async def get_pool(self) -> asyncpg.Pool:
        """
        Get or create connection pool.
        
        Returns:
            asyncpg.Pool: Connection pool instance
        """
        if self._pool is None:
            self._pool = await self._create_pool()
        return self._pool

    async def _create_pool(self) -> asyncpg.Pool:
        """
        Create a new connection pool.
        
        Returns:
            asyncpg.Pool: New connection pool instance
        """
        try:
            pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=60
            )
            return pool
        except Exception as e:
            raise ConnectionError(f"Failed to create PostgreSQL connection pool: {str(e)}")

    async def close(self):
        """Close the connection pool"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def get_database_url(self) -> str:
        """
        Get database URL for SQLAlchemy or other ORMs.
        
        Returns:
            str: Database connection URL
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Singleton instance
_connection = PostgreSQLConnection()


@lru_cache()
def get_postgresql_connection() -> PostgreSQLConnection:
    """
    FastAPI dependency for PostgreSQL connection.
    Uses caching to return the same instance.
    
    Returns:
        PostgreSQLConnection: PostgreSQL connection instance
    """
    return _connection


async def get_postgresql_pool() -> asyncpg.Pool:
    """
    FastAPI dependency for PostgreSQL connection pool.
    Can be injected into route handlers.
    
    Usage:
        @app.get("/patients")
        async def get_patients(pool: asyncpg.Pool = Depends(get_postgresql_pool)):
            # Use pool here
            pass
    
    Returns:
        asyncpg.Pool: PostgreSQL connection pool
    """
    return await _connection.get_pool()


@contextmanager
def postgresql_session():
    """
    Context manager for PostgreSQL operations.
    Ensures proper resource cleanup.
    
    Usage:
        async with postgresql_session() as conn:
            result = await conn.fetch("SELECT * FROM table")
    
    Yields:
        asyncpg.Connection: PostgreSQL connection instance
    """
    async def _session():
        pool = await get_postgresql_pool()
        async with pool.acquire() as connection:
            yield connection
    
    return _session()
