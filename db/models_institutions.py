"""
FARVS Database Models - Institutions Management
===============================================

This module provides database operations for managing institution records
in the FARVS system.

Structure:
- InstitutionsModel: Main class for institutions CRUD operations
- Data validation: Input validation and error handling
- Database queries: SQL operations for institutions
- Error handling: Database connection and query error management
"""

import pyodbc
from typing import Optional, List, Dict, Any

from db.db_connect import get_connection


class InstitutionsModel:
    """
    Database model for managing institution records.
    
    Provides CRUD operations for the Institutions table:
    - Create: Add new institution records
    - Read: Retrieve institution records
    - Update: Modify existing institution records
    - Delete: Remove institution records (with constraint checking)
    """
    
    def __init__(self):
        """Initialize the InstitutionsModel."""
        self.table_name = "Institutions"
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new institution record.
        
        Args:
            data: Dictionary containing institution record data
                - Name (required): Institution name
                - Type (optional): Institution type (Bank, Insurance, etc.)
                - Contact (optional): Contact information
        
        Returns:
            int: The ID of the newly created record
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('Name'):
            raise ValueError("Name is required")
        
        # Prepare SQL query
        query = """
        INSERT INTO Institutions (Name, Type, Contact)
        OUTPUT INSERTED.InstitutionId
        VALUES (?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data['Name'],
            data.get('Type'),
            data.get('Contact')
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create institution record: {e}")
    
    def get_by_id(self, institution_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve an institution record by ID.
        
        Args:
            institution_id: The ID of the institution record
        
        Returns:
            Dict containing the institution record data, or None if not found
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT InstitutionId, Name, Type, Contact
        FROM Institutions
        WHERE InstitutionId = ?
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (institution_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'InstitutionId': row[0],
                        'Name': row[1],
                        'Type': row[2],
                        'Contact': row[3]
                    }
                return None
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve institution record: {e}")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all institution records.
        
        Returns:
            List of dictionaries containing institution record data
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT InstitutionId, Name, Type, Contact
        FROM Institutions
        ORDER BY Name
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'InstitutionId': row[0],
                        'Name': row[1],
                        'Type': row[2],
                        'Contact': row[3]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve institution records: {e}")
    
    def get_by_type(self, institution_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve institutions by type.
        
        Args:
            institution_type: The type of institution to filter by
        
        Returns:
            List of dictionaries containing institution records of the specified type
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT InstitutionId, Name, Type, Contact
        FROM Institutions
        WHERE Type = ?
        ORDER BY Name
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (institution_type,))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'InstitutionId': row[0],
                        'Name': row[1],
                        'Type': row[2],
                        'Contact': row[3]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve institutions by type: {e}")
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search institution records by name or type.
        
        Args:
            search_term: Search term to match against name or type
        
        Returns:
            List of dictionaries containing matching institution records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT InstitutionId, Name, Type, Contact
        FROM Institutions
        WHERE Name LIKE ? OR Type LIKE ?
        ORDER BY Name
        """
        
        search_pattern = f"%{search_term}%"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_pattern, search_pattern))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'InstitutionId': row[0],
                        'Name': row[1],
                        'Type': row[2],
                        'Contact': row[3]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to search institution records: {e}")
    
    def update(self, institution_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing institution record.
        
        Args:
            institution_id: The ID of the institution record to update
            data: Dictionary containing updated institution record data
        
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('Name'):
            raise ValueError("Name is required")
        
        # Prepare SQL query
        query = """
        UPDATE Institutions
        SET Name = ?, Type = ?, Contact = ?
        WHERE InstitutionId = ?
        """
        
        # Prepare parameters
        params = (
            data['Name'],
            data.get('Type'),
            data.get('Contact'),
            institution_id
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update institution record: {e}")
    
    def delete(self, institution_id: int) -> bool:
        """
        Delete an institution record.
        
        Note: This will fail if the institution has associated assets.
        
        Args:
            institution_id: The ID of the institution record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "DELETE FROM Institutions WHERE InstitutionId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (institution_id,))
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to delete institution record: {e}")
    
    def has_assets(self, institution_id: int) -> bool:
        """
        Check if an institution has associated assets.
        
        Args:
            institution_id: The ID of the institution
        
        Returns:
            bool: True if institution has assets, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Assets WHERE InstitutionId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (institution_id,))
                result = cursor.fetchone()
                return result[0] > 0 if result else False
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to check institution assets: {e}")
    
    def count(self) -> int:
        """
        Get the total count of institution records.
        
        Returns:
            int: Total number of institution records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Institutions"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count institution records: {e}")
    
    def get_with_assets_count(self) -> List[Dict[str, Any]]:
        """
        Get institutions with asset counts.
        
        Returns:
            List of dictionaries containing institutions with asset counts
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT i.InstitutionId, i.Name, i.Type, i.Contact,
               COUNT(a.AssetId) as AssetCount
        FROM Institutions i
        LEFT JOIN Assets a ON i.InstitutionId = a.InstitutionId
        GROUP BY i.InstitutionId, i.Name, i.Type, i.Contact
        ORDER BY i.Name
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'InstitutionId': row[0],
                        'Name': row[1],
                        'Type': row[2],
                        'Contact': row[3],
                        'AssetCount': row[4]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve institutions with asset count: {e}")
