"""
Base Repository Pattern for PostgreSQL Operations
Provides common CRUD operations for all tables
"""
from typing import List, Dict, Any, Optional, Union
import asyncpg
from datetime import datetime
import json
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """
    Base repository class for PostgreSQL operations.
    Implements common CRUD operations that can be used across all tables.
    """

    def __init__(self, pool: asyncpg.Pool, table_name: str):
        """
        Initialize repository.

        Args:
            pool: PostgreSQL connection pool
            table_name: Name of the table
        """
        self.pool = pool
        self.table_name = table_name

    async def _execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            List of dictionaries containing query results
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]

    async def _execute_command(self, query: str, *args) -> str:
        """
        Execute a command (INSERT, UPDATE, DELETE) and return status.

        Args:
            query: SQL command string
            *args: Query parameters

        Returns:
            Command status
        """
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single record.

        Args:
            data: Dictionary containing record data

        Returns:
            Inserted record data
        """
        # Add timestamps
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()

        # Build INSERT query
        columns = list(data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = list(data.values())

        # Convert complex types to JSON strings
        for i, value in enumerate(values):
            if isinstance(value, (dict, list)):
                values[i] = json.dumps(value)

        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """

        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *values)
            return dict(row) if row else data

    async def insert_many(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Insert multiple records.

        Args:
            records: List of dictionaries containing record data

        Returns:
            List of inserted records
        """
        if not records:
            return []

        # Add timestamps to all records
        for record in records:
            record['created_at'] = datetime.utcnow()
            record['updated_at'] = datetime.utcnow()

        # Get columns from first record
        columns = list(records[0].keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]

        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """

        results = []
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                for record in records:
                    values = list(record.values())
                    # Convert complex types to JSON strings
                    for i, value in enumerate(values):
                        if isinstance(value, (dict, list)):
                            values[i] = json.dumps(value)
                    
                    row = await connection.fetchrow(query, *values)
                    if row:
                        results.append(dict(row))

        return results

    async def find_by_id(self, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Find a record by ID.

        Args:
            id_field: Name of the ID field (e.g., 'patient_id')
            id_value: Value of the ID

        Returns:
            Record dictionary or None if not found
        """
        query = f"SELECT * FROM {self.table_name} WHERE {id_field} = $1 LIMIT 1"
        
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, id_value)
            return dict(row) if row else None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all records with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of record dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """

        return await self._execute_query(query, limit, offset)

    async def find_by_filter(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find records by multiple filters.

        Args:
            filters: Dictionary of field-value pairs to filter by
            limit: Maximum number of records to return

        Returns:
            List of matching records
        """
        if not filters:
            return await self.find_all(limit)

        where_clauses = []
        values = []

        for i, (field, value) in enumerate(filters.items(), 1):
            where_clauses.append(f"{field} = ${i}")
            values.append(value)

        where_clause = " AND ".join(where_clauses)
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {where_clause}
            LIMIT ${len(values) + 1}
        """
        values.append(limit)

        return await self._execute_query(query, *values)

    async def update(self, id_field: str, id_value: str, data: Dict[str, Any]) -> bool:
        """
        Update a record.

        Args:
            id_field: Name of the ID field
            id_value: Value of the ID
            data: Dictionary containing fields to update

        Returns:
            True if update was successful
        """
        if not data:
            return False

        # Add updated timestamp
        data['updated_at'] = datetime.utcnow()

        # Build SET clause
        set_clauses = []
        values = []

        for i, (field, value) in enumerate(data.items(), 1):
            set_clauses.append(f"{field} = ${i}")
            # Convert complex types to JSON strings
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            values.append(value)

        set_clause = ", ".join(set_clauses)
        values.append(id_value)  # Add ID value for WHERE clause

        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {id_field} = ${len(values)}
        """

        result = await self._execute_command(query, *values)
        return "UPDATE 1" in result

    async def delete(self, id_field: str, id_value: str) -> bool:
        """
        Delete a record (hard delete).

        Args:
            id_field: Name of the ID field
            id_value: Value of the ID

        Returns:
            True if deletion was successful
        """
        query = f"DELETE FROM {self.table_name} WHERE {id_field} = $1"
        result = await self._execute_command(query, id_value)
        return "DELETE 1" in result

    async def soft_delete(self, id_field: str, id_value: str) -> bool:
        """
        Soft delete a record by setting is_active to False.

        Args:
            id_field: Name of the ID field
            id_value: Value of the ID

        Returns:
            True if soft delete was successful
        """
        return await self.update(id_field, id_value, {"is_active": False})

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records, optionally with filters.

        Args:
            filters: Optional dictionary of field-value pairs to filter by

        Returns:
            Count of records
        """
        if filters:
            where_clauses = []
            values = []

            for i, (field, value) in enumerate(filters.items(), 1):
                where_clauses.append(f"{field} = ${i}")
                values.append(value)

            where_clause = " AND ".join(where_clauses)
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {where_clause}"
            results = await self._execute_query(query, *values)
        else:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            results = await self._execute_query(query)

        return results[0]['count'] if results else 0

    async def execute_custom_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Execute a custom query.

        Args:
            query: Custom SQL query
            *args: Query parameters

        Returns:
            Query results as list of dictionaries
        """
        return await self._execute_query(query, *args)

    async def search(self, search_fields: List[str], search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search records across multiple fields using ILIKE.

        Args:
            search_fields: List of field names to search in
            search_term: Search term
            limit: Maximum number of results

        Returns:
            List of matching records
        """
        if not search_fields or not search_term:
            return []

        # Build search conditions
        search_conditions = []
        for i, field in enumerate(search_fields, 1):
            search_conditions.append(f"LOWER({field}) LIKE ${i}")

        where_clause = " OR ".join(search_conditions)
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${len(search_fields) + 1}
        """

        # Prepare search values (add wildcards)
        search_values = [f"%{search_term.lower()}%"] * len(search_fields)
        search_values.append(limit)

        return await self._execute_query(query, *search_values)
