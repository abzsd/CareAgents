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
    ssl: Optional[str] = Field(default=None)  # "require", "verify-ca", "verify-full", or None
    timeout: Optional[float] = Field(default=60.0)  # Connection timeout
    command_timeout: Optional[float] = Field(default=60.0)  # Command timeout


class PostgresToolkit:
    """PostgreSQL toolkit for agents"""

    def __init__(self, config: PostgresConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool"""
        if self.pool is None:
            # Build connection parameters
            pool_kwargs = {
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "user": self.config.user,
                "password": self.config.password,
                "min_size": 2,
                "max_size": 10,
            }

            # Add SSL if configured
            if self.config.ssl:
                import ssl as ssl_module
                if self.config.ssl == "require":
                    # Create SSL context that doesn't verify certificates
                    ssl_context = ssl_module.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl_module.CERT_NONE
                    pool_kwargs["ssl"] = ssl_context
                elif self.config.ssl in ["verify-ca", "verify-full"]:
                    # Use default SSL context with verification
                    pool_kwargs["ssl"] = ssl_module.create_default_context()

            # Add timeouts if configured
            if self.config.timeout:
                pool_kwargs["timeout"] = self.config.timeout
            if self.config.command_timeout:
                pool_kwargs["command_timeout"] = self.config.command_timeout

            self.pool = await asyncpg.create_pool(**pool_kwargs)
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



