"""
FARVS Database Models - Deceased Records
========================================

This module provides database operations for managing deceased person records
in the FARVS system.

Structure:
- DeceasedModel: Main class for deceased records CRUD operations
- Data validation: Input validation and error handling
- Database queries: SQL operations for deceased records
- Error handling: Database connection and query error management
"""

import pyodbc
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from db.db_connect import get_connection


class DeceasedModel:
    """
    Database model for managing deceased person records.
    
    Provides CRUD operations for the Deceased table:
    - Create: Add new deceased records
    - Read: Retrieve deceased records with filtering
    - Update: Modify existing deceased records
    - Delete: Remove deceased records (with cascade handling)
    """
    
    def __init__(self):
        """Initialize the DeceasedModel."""
        self.table_name = "Deceased"
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new deceased record.
        
        Args:
            data: Dictionary containing deceased record data
                - NationalId (optional): National ID number
                - FirstName (required): First name
                - LastName (required): Last name
                - DateOfBirth (optional): Date of birth (YYYY-MM-DD)
                - DateOfDeath (optional): Date of death (YYYY-MM-DD)
        
        Returns:
            int: The ID of the newly created record
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('FirstName'):
            raise ValueError("FirstName is required")
        if not data.get('LastName'):
            raise ValueError("LastName is required")
        
        # Prepare SQL query
        query = """
        INSERT INTO Deceased (NationalId, FirstName, LastName, DateOfBirth, DateOfDeath)
        OUTPUT INSERTED.DeceasedId
        VALUES (?, ?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data['LastName'],
            data.get('DateOfBirth'),
            data.get('DateOfDeath')
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create deceased record: {e}")
    
    def get_by_id(self, deceased_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a deceased record by ID.
        
        Args:
            deceased_id: The ID of the deceased record
        
        Returns:
            Dict containing the deceased record data, or None if not found
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT DeceasedId, NationalId, FirstName, LastName, DateOfBirth, DateOfDeath, CreatedAt
        FROM Deceased
        WHERE DeceasedId = ?
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (deceased_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'DeceasedId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'DateOfBirth': row[4],
                        'DateOfDeath': row[5],
                        'CreatedAt': row[6]
                    }
                return None
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve deceased record: {e}")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all deceased records.
        
        Returns:
            List of dictionaries containing deceased record data
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT DeceasedId, NationalId, FirstName, LastName, DateOfBirth, DateOfDeath, CreatedAt
        FROM Deceased
        ORDER BY LastName, FirstName
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'DeceasedId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'DateOfBirth': row[4],
                        'DateOfDeath': row[5],
                        'CreatedAt': row[6]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve deceased records: {e}")
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search deceased records by name or national ID.
        
        Args:
            search_term: Search term to match against names or national ID
        
        Returns:
            List of dictionaries containing matching deceased records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT DeceasedId, NationalId, FirstName, LastName, DateOfBirth, DateOfDeath, CreatedAt
        FROM Deceased
        WHERE FirstName LIKE ? OR LastName LIKE ? OR NationalId LIKE ?
        ORDER BY LastName, FirstName
        """
        
        search_pattern = f"%{search_term}%"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'DeceasedId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'DateOfBirth': row[4],
                        'DateOfDeath': row[5],
                        'CreatedAt': row[6]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to search deceased records: {e}")
    
    def update(self, deceased_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing deceased record.
        
        Args:
            deceased_id: The ID of the deceased record to update
            data: Dictionary containing updated deceased record data
        
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('FirstName'):
            raise ValueError("FirstName is required")
        if not data.get('LastName'):
            raise ValueError("LastName is required")
        
        # Prepare SQL query
        query = """
        UPDATE Deceased
        SET NationalId = ?, FirstName = ?, LastName = ?, DateOfBirth = ?, DateOfDeath = ?
        WHERE DeceasedId = ?
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data['LastName'],
            data.get('DateOfBirth'),
            data.get('DateOfDeath'),
            deceased_id
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update deceased record: {e}")
    
    def delete(self, deceased_id: int) -> bool:
        """
        Delete a deceased record.
        
        Note: This will cascade delete associated assets and claims.
        
        Args:
            deceased_id: The ID of the deceased record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "DELETE FROM Deceased WHERE DeceasedId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (deceased_id,))
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to delete deceased record: {e}")
    
    def count(self) -> int:
        """
        Get the total count of deceased records.
        
        Returns:
            int: Total number of deceased records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Deceased"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count deceased records: {e}")
    
    def get_with_assets_count(self) -> List[Dict[str, Any]]:
        """
        Get deceased records with asset count.
        
        Returns:
            List of dictionaries containing deceased records with asset counts
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT d.DeceasedId, d.NationalId, d.FirstName, d.LastName, d.DateOfBirth, d.DateOfDeath,
               COUNT(a.AssetId) as AssetCount
        FROM Deceased d
        LEFT JOIN Assets a ON d.DeceasedId = a.DeceasedId
        GROUP BY d.DeceasedId, d.NationalId, d.FirstName, d.LastName, d.DateOfBirth, d.DateOfDeath
        ORDER BY d.LastName, d.FirstName
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'DeceasedId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'DateOfBirth': row[4],
                        'DateOfDeath': row[5],
                        'AssetCount': row[6]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve deceased records with asset count: {e}")
