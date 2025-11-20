"""
FARVS Database Models - Claimants Management
=============================================

This module provides database operations for managing claimant records
in the FARVS system.

Structure:
- ClaimantsModel: Main class for claimants CRUD operations
- Data validation: Input validation and error handling
- Database queries: SQL operations for claimants
- Error handling: Database connection and query error management
"""

import pyodbc
from typing import Optional, List, Dict, Any

from db.db_connect import get_connection


class ClaimantsModel:
    """
    Database model for managing claimant records.
    
    Provides CRUD operations for the Claimants table:
    - Create: Add new claimant records
    - Read: Retrieve claimant records
    - Update: Modify existing claimant records
    - Delete: Remove claimant records (with constraint checking)
    """
    
    def __init__(self):
        """Initialize the ClaimantsModel."""
        self.table_name = "Claimants"
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new claimant record.
        
        Args:
            data: Dictionary containing claimant record data
                - NationalId (optional): National ID number
                - FirstName (required): First name
                - LastName (required): Last name
                - Relationship (optional): Relationship to deceased
                - Contact (optional): Contact information
        
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
        INSERT INTO Claimants (NationalId, FirstName, MiddleName, LastName, DateOfBirth, Gender,
            Relationship, Contact, Email, Phone, Address, Occupation, MaritalStatus,
            AlternateContact, RelationshipProof, Notes)
        OUTPUT INSERTED.ClaimantId
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data.get('MiddleName'),
            data['LastName'],
            data.get('DateOfBirth'),
            data.get('Gender'),
            data.get('Relationship'),
            data.get('Contact'),
            data.get('Email'),
            data.get('Phone'),
            data.get('Address'),
            data.get('Occupation'),
            data.get('MaritalStatus'),
            data.get('AlternateContact'),
            data.get('RelationshipProof'),
            data.get('Notes')
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create claimant record: {e}")
    
    def get_by_id(self, claimant_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a claimant record by ID.
        
        Args:
            claimant_id: The ID of the claimant record
        
        Returns:
            Dict containing the claimant record data, or None if not found
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT ClaimantId, NationalId, FirstName, MiddleName, LastName, DateOfBirth, Gender,
            Relationship, Contact, Email, Phone, Address, Occupation, MaritalStatus,
            AlternateContact, RelationshipProof, Notes, CreatedAt
        FROM Claimants
        WHERE ClaimantId = ?
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (claimant_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'ClaimantId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'MiddleName': row[3],
                        'LastName': row[4],
                        'DateOfBirth': row[5],
                        'Gender': row[6],
                        'Relationship': row[7],
                        'Contact': row[8],
                        'Email': row[9],
                        'Phone': row[10],
                        'Address': row[11],
                        'Occupation': row[12],
                        'MaritalStatus': row[13],
                        'AlternateContact': row[14],
                        'RelationshipProof': row[15],
                        'Notes': row[16],
                        'CreatedAt': row[17]
                    }
                return None
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claimant record: {e}")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all claimant records.
        
        Returns:
            List of dictionaries containing claimant record data
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT ClaimantId, NationalId, FirstName, MiddleName, LastName, DateOfBirth, Gender,
            Relationship, Contact, Email, Phone, Address, Occupation, MaritalStatus,
            AlternateContact, RelationshipProof, Notes, CreatedAt
        FROM Claimants
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
                        'ClaimantId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'MiddleName': row[3],
                        'LastName': row[4],
                        'DateOfBirth': row[5],
                        'Gender': row[6],
                        'Relationship': row[7],
                        'Contact': row[8],
                        'Email': row[9],
                        'Phone': row[10],
                        'Address': row[11],
                        'Occupation': row[12],
                        'MaritalStatus': row[13],
                        'AlternateContact': row[14],
                        'RelationshipProof': row[15],
                        'Notes': row[16],
                        'CreatedAt': row[17]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claimant records: {e}")
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search claimant records by name or national ID.
        
        Args:
            search_term: Search term to match against names or national ID
        
        Returns:
            List of dictionaries containing matching claimant records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT ClaimantId, NationalId, FirstName, MiddleName, LastName, DateOfBirth, Gender,
            Relationship, Contact, Email, Phone, Address, Occupation, MaritalStatus,
            AlternateContact, RelationshipProof, Notes, CreatedAt
        FROM Claimants
        WHERE FirstName LIKE ? OR LastName LIKE ? OR NationalId LIKE ? OR MiddleName LIKE ? OR Email LIKE ?
        ORDER BY LastName, FirstName
        """
        
        search_pattern = f"%{search_term}%"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'ClaimantId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'MiddleName': row[3],
                        'LastName': row[4],
                        'DateOfBirth': row[5],
                        'Gender': row[6],
                        'Relationship': row[7],
                        'Contact': row[8],
                        'Email': row[9],
                        'Phone': row[10],
                        'Address': row[11],
                        'Occupation': row[12],
                        'MaritalStatus': row[13],
                        'AlternateContact': row[14],
                        'RelationshipProof': row[15],
                        'Notes': row[16],
                        'CreatedAt': row[17]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to search claimant records: {e}")
    
    def update(self, claimant_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing claimant record.
        
        Args:
            claimant_id: The ID of the claimant record to update
            data: Dictionary containing updated claimant record data
        
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
        UPDATE Claimants
        SET NationalId = ?, FirstName = ?, MiddleName = ?, LastName = ?, DateOfBirth = ?, Gender = ?,
            Relationship = ?, Contact = ?, Email = ?, Phone = ?, Address = ?, Occupation = ?,
            MaritalStatus = ?, AlternateContact = ?, RelationshipProof = ?, Notes = ?
        WHERE ClaimantId = ?
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data.get('MiddleName'),
            data['LastName'],
            data.get('DateOfBirth'),
            data.get('Gender'),
            data.get('Relationship'),
            data.get('Contact'),
            data.get('Email'),
            data.get('Phone'),
            data.get('Address'),
            data.get('Occupation'),
            data.get('MaritalStatus'),
            data.get('AlternateContact'),
            data.get('RelationshipProof'),
            data.get('Notes'),
            claimant_id
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update claimant record: {e}")
    
    def delete(self, claimant_id: int) -> bool:
        """
        Delete a claimant record.
        
        Note: This will fail if the claimant has associated claims.
        
        Args:
            claimant_id: The ID of the claimant record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "DELETE FROM Claimants WHERE ClaimantId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (claimant_id,))
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to delete claimant record: {e}")
    
    def has_claims(self, claimant_id: int) -> bool:
        """
        Check if a claimant has associated claims.
        
        Args:
            claimant_id: The ID of the claimant
        
        Returns:
            bool: True if claimant has claims, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Claims WHERE ClaimantId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (claimant_id,))
                result = cursor.fetchone()
                return result[0] > 0 if result else False
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to check claimant claims: {e}")
    
    def count(self) -> int:
        """
        Get the total count of claimant records.
        
        Returns:
            int: Total number of claimant records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Claimants"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count claimant records: {e}")
    
    def get_with_claims_count(self) -> List[Dict[str, Any]]:
        """
        Get claimants with claim counts.
        
        Returns:
            List of dictionaries containing claimants with claim counts
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT c.ClaimantId, c.NationalId, c.FirstName, c.LastName, c.Relationship, c.Contact,
               COUNT(cl.ClaimId) as ClaimCount
        FROM Claimants c
        LEFT JOIN Claims cl ON c.ClaimantId = cl.ClaimantId
        GROUP BY c.ClaimantId, c.NationalId, c.FirstName, c.LastName, c.Relationship, c.Contact
        ORDER BY c.LastName, c.FirstName
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'ClaimantId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'Relationship': row[4],
                        'Contact': row[5],
                        'ClaimCount': row[6]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claimants with claim count: {e}")
