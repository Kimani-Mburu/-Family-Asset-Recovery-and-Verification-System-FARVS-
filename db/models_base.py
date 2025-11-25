"""
FARVS Database Models - Base Model Class
=========================================

This module provides a base class for all database models to reduce code duplication
and standardize common CRUD operations.

All models inherit from BaseModel which provides:
- Common connection handling
- Standardized error handling
- Row-to-dict conversion utilities
- Common query execution patterns
"""

import pyodbc
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod

from db.db_connect import get_connection


class BaseModel(ABC):
    """
    Base class for all database models.
    
    Provides common functionality for:
    - Database connection management
    - Error handling
    - Row-to-dict conversion
    - Common query patterns
    """
    
    def __init__(self, table_name: str):
        """
        Initialize the base model.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
        self._id_column = f"{table_name.rstrip('s')}Id"  # e.g., "Deceased" -> "DeceasedId"
    
    def _execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Execute a database query with standardized error handling.
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            fetch_one: If True, fetch one row
            fetch_all: If True, fetch all rows
            
        Returns:
            Query result (row, rows, or rowcount)
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
                    
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Database operation failed on {self.table_name}: {e}")
    
    def _row_to_dict(self, row: Tuple, columns: List[str]) -> Dict[str, Any]:
        """
        Convert a database row tuple to a dictionary.
        
        Args:
            row: Database row tuple
            columns: List of column names
            
        Returns:
            Dictionary with column names as keys
        """
        return {col: row[i] if i < len(row) else None for i, col in enumerate(columns)}
    
    def _rows_to_dicts(self, rows: List[Tuple], columns: List[str]) -> List[Dict[str, Any]]:
        """
        Convert multiple database rows to dictionaries.
        
        Args:
            rows: List of database row tuples
            columns: List of column names
            
        Returns:
            List of dictionaries
        """
        return [self._row_to_dict(row, columns) for row in rows]
    
    def count(self) -> int:
        """
        Get the total count of records in the table.
        
        Returns:
            int: Total number of records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self._execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def delete(self, record_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: The ID of the record to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = f"DELETE FROM {self.table_name} WHERE {self._id_column} = ?"
        rowcount = self._execute_query(query, (record_id,))
        return rowcount > 0
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new record. Must be implemented by subclasses.
        
        Args:
            data: Dictionary containing record data
            
        Returns:
            int: The ID of the newly created record
        """
        pass
    
    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record by ID. Must be implemented by subclasses.
        
        Args:
            record_id: The ID of the record
            
        Returns:
            Dict containing the record data, or None if not found
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all records. Must be implemented by subclasses.
        
        Returns:
            List of dictionaries containing record data
        """
        pass
    
    @abstractmethod
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing record. Must be implemented by subclasses.
        
        Args:
            record_id: The ID of the record to update
            data: Dictionary containing updated record data
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        pass

