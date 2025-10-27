"""
FARVS Database Models - Claims Management
=========================================

This module provides database operations for managing claims and claimants
in the FARVS system.

Structure:
- ClaimsModel: Main class for claims CRUD operations
- ClaimantsModel: Main class for claimants CRUD operations
- Data validation: Input validation and relationship integrity
- Database queries: SQL operations for claims with joins
- Error handling: Database connection and query error management
"""

import pyodbc
from typing import Optional, List, Dict, Any
from datetime import datetime

from db.db_connect import get_connection


class ClaimsModel:
    """
    Database model for managing claim records.
    
    Provides CRUD operations for the Claims table:
    - Create: Add new claims linked to assets and claimants
    - Read: Retrieve claims with detailed information
    - Update: Modify existing claim records and status
    - Delete: Remove claim records
    """
    
    def __init__(self):
        """Initialize the ClaimsModel."""
        self.table_name = "Claims"
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new claim record.
        
        Args:
            data: Dictionary containing claim record data
                - AssetId (required): ID of the asset being claimed
                - ClaimantId (required): ID of the claimant
                - Status (optional): Claim status (default: 'Pending')
                - Notes (optional): Additional notes
        
        Returns:
            int: The ID of the newly created record
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('AssetId'):
            raise ValueError("AssetId is required")
        if not data.get('ClaimantId'):
            raise ValueError("ClaimantId is required")
        
        # Prepare SQL query
        query = """
        INSERT INTO Claims (AssetId, ClaimantId, Status, Notes)
        OUTPUT INSERTED.ClaimId
        VALUES (?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data['AssetId'],
            data['ClaimantId'],
            data.get('Status', 'Pending'),
            data.get('Notes')
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create claim record: {e}")
    
    def get_by_id(self, claim_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a claim record by ID with detailed information.
        
        Args:
            claim_id: The ID of the claim record
        
        Returns:
            Dict containing the claim record data with joins, or None if not found
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT c.ClaimId, c.AssetId, c.ClaimantId, c.Status, c.FiledAt, 
               c.VerifiedAt, c.SettledAt, c.Notes,
               a.AssetType, a.Identifier, a.EstimatedValue,
               d.FirstName as DeceasedFirstName, d.LastName as DeceasedLastName,
               cl.FirstName as ClaimantFirstName, cl.LastName as ClaimantLastName,
               i.Name as InstitutionName
        FROM Claims c
        INNER JOIN Assets a ON c.AssetId = a.AssetId
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Claimants cl ON c.ClaimantId = cl.ClaimantId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE c.ClaimId = ?
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (claim_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'ClaimId': row[0],
                        'AssetId': row[1],
                        'ClaimantId': row[2],
                        'Status': row[3],
                        'FiledAt': row[4],
                        'VerifiedAt': row[5],
                        'SettledAt': row[6],
                        'Notes': row[7],
                        'AssetType': row[8],
                        'AssetIdentifier': row[9],
                        'AssetValue': row[10],
                        'DeceasedName': f"{row[11]} {row[12]}",
                        'ClaimantName': f"{row[13]} {row[14]}",
                        'InstitutionName': row[15]
                    }
                return None
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claim record: {e}")
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve all claim records with detailed information.
        
        Returns:
            List of dictionaries containing claim records with joins
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT c.ClaimId, c.AssetId, c.ClaimantId, c.Status, c.FiledAt, 
               c.VerifiedAt, c.SettledAt, c.Notes,
               a.AssetType, a.Identifier, a.EstimatedValue,
               d.FirstName as DeceasedFirstName, d.LastName as DeceasedLastName,
               cl.FirstName as ClaimantFirstName, cl.LastName as ClaimantLastName,
               i.Name as InstitutionName
        FROM Claims c
        INNER JOIN Assets a ON c.AssetId = a.AssetId
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Claimants cl ON c.ClaimantId = cl.ClaimantId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        ORDER BY c.FiledAt DESC
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'ClaimId': row[0],
                        'AssetId': row[1],
                        'ClaimantId': row[2],
                        'Status': row[3],
                        'FiledAt': row[4],
                        'VerifiedAt': row[5],
                        'SettledAt': row[6],
                        'Notes': row[7],
                        'AssetType': row[8],
                        'AssetIdentifier': row[9],
                        'AssetValue': row[10],
                        'DeceasedName': f"{row[11]} {row[12]}",
                        'ClaimantName': f"{row[13]} {row[14]}",
                        'InstitutionName': row[15]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claim records: {e}")
    
    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Retrieve claims by status.
        
        Args:
            status: The status to filter by ('Pending', 'Verified', 'Settled')
        
        Returns:
            List of dictionaries containing claim records with the specified status
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT c.ClaimId, c.AssetId, c.ClaimantId, c.Status, c.FiledAt, 
               c.VerifiedAt, c.SettledAt, c.Notes,
               a.AssetType, a.Identifier, a.EstimatedValue,
               d.FirstName as DeceasedFirstName, d.LastName as DeceasedLastName,
               cl.FirstName as ClaimantFirstName, cl.LastName as ClaimantLastName,
               i.Name as InstitutionName
        FROM Claims c
        INNER JOIN Assets a ON c.AssetId = a.AssetId
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Claimants cl ON c.ClaimantId = cl.ClaimantId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE c.Status = ?
        ORDER BY c.FiledAt DESC
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (status,))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'ClaimId': row[0],
                        'AssetId': row[1],
                        'ClaimantId': row[2],
                        'Status': row[3],
                        'FiledAt': row[4],
                        'VerifiedAt': row[5],
                        'SettledAt': row[6],
                        'Notes': row[7],
                        'AssetType': row[8],
                        'AssetIdentifier': row[9],
                        'AssetValue': row[10],
                        'DeceasedName': f"{row[11]} {row[12]}",
                        'ClaimantName': f"{row[13]} {row[14]}",
                        'InstitutionName': row[15]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claims by status: {e}")
    
    def update(self, claim_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing claim record.
        
        Args:
            claim_id: The ID of the claim record to update
            data: Dictionary containing updated claim record data
        
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('AssetId'):
            raise ValueError("AssetId is required")
        if not data.get('ClaimantId'):
            raise ValueError("ClaimantId is required")
        if not data.get('Status'):
            raise ValueError("Status is required")
        
        # Prepare SQL query
        query = """
        UPDATE Claims
        SET AssetId = ?, ClaimantId = ?, Status = ?, Notes = ?, 
            VerifiedAt = ?, SettledAt = ?
        WHERE ClaimId = ?
        """
        
        # Prepare parameters
        params = (
            data['AssetId'],
            data['ClaimantId'],
            data['Status'],
            data.get('Notes'),
            data.get('VerifiedAt'),
            data.get('SettledAt'),
            claim_id
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update claim record: {e}")
    
    def update_status(self, claim_id: int, status: str, notes: Optional[str] = None) -> bool:
        """
        Update only the status of a claim record.
        
        Args:
            claim_id: The ID of the claim record to update
            status: New status ('Pending', 'Verified', 'Settled')
            notes: Optional notes to add
        
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        # Determine which timestamp to update based on status
        timestamp_field = ""
        timestamp_value = None
        
        if status == 'Verified':
            timestamp_field = ", VerifiedAt = ?"
            timestamp_value = datetime.now()
        elif status == 'Settled':
            timestamp_field = ", SettledAt = ?"
            timestamp_value = datetime.now()
        
        query = f"""
        UPDATE Claims
        SET Status = ?, Notes = ?{timestamp_field}
        WHERE ClaimId = ?
        """
        
        params = [status, notes]
        if timestamp_value:
            params.append(timestamp_value)
        params.append(claim_id)
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update claim status: {e}")
    
    def delete(self, claim_id: int) -> bool:
        """
        Delete a claim record.
        
        Args:
            claim_id: The ID of the claim record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "DELETE FROM Claims WHERE ClaimId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (claim_id,))
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to delete claim record: {e}")
    
    def count(self) -> int:
        """
        Get the total count of claim records.
        
        Returns:
            int: Total number of claim records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Claims"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count claim records: {e}")
    
    def count_by_status(self, status: str) -> int:
        """
        Get the count of claims by status.
        
        Args:
            status: The status to count ('Pending', 'Verified', 'Settled')
        
        Returns:
            int: Number of claims with the specified status
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Claims WHERE Status = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (status,))
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count claims by status: {e}")


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
        INSERT INTO Claimants (NationalId, FirstName, LastName, Relationship, Contact)
        OUTPUT INSERTED.ClaimantId
        VALUES (?, ?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data['LastName'],
            data.get('Relationship'),
            data.get('Contact')
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
        SELECT ClaimantId, NationalId, FirstName, LastName, Relationship, Contact
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
                        'LastName': row[3],
                        'Relationship': row[4],
                        'Contact': row[5]
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
        SELECT ClaimantId, NationalId, FirstName, LastName, Relationship, Contact
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
                        'LastName': row[3],
                        'Relationship': row[4],
                        'Contact': row[5]
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
        SELECT ClaimantId, NationalId, FirstName, LastName, Relationship, Contact
        FROM Claimants
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
                        'ClaimantId': row[0],
                        'NationalId': row[1],
                        'FirstName': row[2],
                        'LastName': row[3],
                        'Relationship': row[4],
                        'Contact': row[5]
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
        SET NationalId = ?, FirstName = ?, LastName = ?, Relationship = ?, Contact = ?
        WHERE ClaimantId = ?
        """
        
        # Prepare parameters
        params = (
            data.get('NationalId'),
            data['FirstName'],
            data['LastName'],
            data.get('Relationship'),
            data.get('Contact'),
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
