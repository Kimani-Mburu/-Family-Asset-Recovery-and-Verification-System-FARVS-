"""
FARVS Database Models - Assets Management
=========================================

This module provides database operations for managing asset records
linked to deceased persons in the FARVS system.

Structure:
- AssetsModel: Main class for assets CRUD operations
- Data validation: Input validation and relationship integrity
- Database queries: SQL operations for assets with joins
- Error handling: Database connection and query error management
"""

import pyodbc
from typing import Optional, List, Dict, Any
from decimal import Decimal

from db.db_connect import get_connection


class AssetsModel:
    """
    Database model for managing asset records.
    
    Provides CRUD operations for the Assets table:
    - Create: Add new assets linked to deceased persons and institutions
    - Read: Retrieve assets with detailed information
    - Update: Modify existing asset records
    - Delete: Remove asset records (with cascade handling)
    """
    
    def __init__(self):
        """Initialize the AssetsModel."""
        self.table_name = "Assets"
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new asset record.
        
        Args:
            data: Dictionary containing asset record data
                - DeceasedId (required): ID of the deceased person
                - InstitutionId (required): ID of the institution
                - AssetType (required): Type of asset
                - Identifier (optional): Account/policy identifier
                - EstimatedValue (optional): Estimated value of the asset
        
        Returns:
            int: The ID of the newly created record
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('DeceasedId'):
            raise ValueError("DeceasedId is required")
        if not data.get('InstitutionId'):
            raise ValueError("InstitutionId is required")
        if not data.get('AssetType'):
            raise ValueError("AssetType is required")
        
        # Prepare SQL query
        query = """
        INSERT INTO Assets (DeceasedId, InstitutionId, AssetType, Identifier, EstimatedValue,
            AccountStatus, AccountOpeningDate, LastTransactionDate, InterestRate, MaturityDate,
            BeneficiaryInfo, AccountHolderName, BranchLocation, Currency, Documentation, Notes)
        OUTPUT INSERTED.AssetId
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = (
            data['DeceasedId'],
            data['InstitutionId'],
            data['AssetType'],
            data.get('Identifier'),
            data.get('EstimatedValue'),
            data.get('AccountStatus'),
            data.get('AccountOpeningDate'),
            data.get('LastTransactionDate'),
            data.get('InterestRate'),
            data.get('MaturityDate'),
            data.get('BeneficiaryInfo'),
            data.get('AccountHolderName'),
            data.get('BranchLocation'),
            data.get('Currency', 'USD'),
            data.get('Documentation'),
            data.get('Notes')
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create asset record: {e}")
    
    def get_by_id(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve an asset record by ID with detailed information.
        
        Args:
            asset_id: The ID of the asset record
        
        Returns:
            Dict containing the asset record data with joins, or None if not found
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.AccountStatus, a.AccountOpeningDate, a.LastTransactionDate,
               a.InterestRate, a.MaturityDate, a.BeneficiaryInfo, a.AccountHolderName,
               a.BranchLocation, a.Currency, a.Documentation, a.Notes, a.CreatedAt,
               d.FirstName, d.LastName,
               i.Name as InstitutionName, i.Type as InstitutionType
        FROM Assets a
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE a.AssetId = ?
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (asset_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'AccountStatus': row[6],
                        'AccountOpeningDate': row[7],
                        'LastTransactionDate': row[8],
                        'InterestRate': row[9],
                        'MaturityDate': row[10],
                        'BeneficiaryInfo': row[11],
                        'AccountHolderName': row[12],
                        'BranchLocation': row[13],
                        'Currency': row[14],
                        'Documentation': row[15],
                        'Notes': row[16],
                        'CreatedAt': row[17],
                        'DeceasedName': f"{row[18]} {row[19]}",
                        'InstitutionName': row[20],
                        'InstitutionType': row[21]
                    }
                return None
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve asset record: {e}")
    
    def get_all_with_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve all asset records with detailed information.
        
        Returns:
            List of dictionaries containing asset records with joins
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.AccountStatus, a.Currency, a.Notes, a.CreatedAt,
               d.FirstName, d.LastName,
               i.Name as InstitutionName, i.Type as InstitutionType
        FROM Assets a
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        ORDER BY d.LastName, d.FirstName, a.AssetType
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'AccountStatus': row[6],
                        'Currency': row[7],
                        'Notes': row[8],
                        'CreatedAt': row[9],
                        'DeceasedName': f"{row[10]} {row[11]}",
                        'InstitutionName': row[12],
                        'InstitutionType': row[13]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve asset records: {e}")
    
    def get_by_deceased_id(self, deceased_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all assets for a specific deceased person.
        
        Args:
            deceased_id: The ID of the deceased person
        
        Returns:
            List of dictionaries containing asset records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.CreatedAt,
               i.Name as InstitutionName, i.Type as InstitutionType
        FROM Assets a
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE a.DeceasedId = ?
        ORDER BY a.AssetType
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (deceased_id,))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'CreatedAt': row[6],
                        'InstitutionName': row[7],
                        'InstitutionType': row[8]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve assets for deceased person: {e}")
    
    def search(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search assets by type, identifier, or deceased person name.
        
        Args:
            search_term: Search term to match against asset data
        
        Returns:
            List of dictionaries containing matching asset records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.CreatedAt,
               d.FirstName, d.LastName,
               i.Name as InstitutionName, i.Type as InstitutionType
        FROM Assets a
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE a.AssetType LIKE ? OR a.Identifier LIKE ? OR d.FirstName LIKE ? OR d.LastName LIKE ?
        ORDER BY d.LastName, d.FirstName, a.AssetType
        """
        
        search_pattern = f"%{search_term}%"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'CreatedAt': row[6],
                        'DeceasedName': f"{row[7]} {row[8]}",
                        'InstitutionName': row[9],
                        'InstitutionType': row[10]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to search asset records: {e}")
    
    def update(self, asset_id: int, data: Dict[str, Any]) -> bool:
        """
        Update an existing asset record.
        
        Args:
            asset_id: The ID of the asset record to update
            data: Dictionary containing updated asset record data
        
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If required fields are missing or invalid
            pyodbc.Error: If database operation fails
        """
        # Validate required fields
        if not data.get('DeceasedId'):
            raise ValueError("DeceasedId is required")
        if not data.get('InstitutionId'):
            raise ValueError("InstitutionId is required")
        if not data.get('AssetType'):
            raise ValueError("AssetType is required")
        
        # Prepare SQL query
        query = """
        UPDATE Assets
        SET DeceasedId = ?, InstitutionId = ?, AssetType = ?, Identifier = ?, EstimatedValue = ?,
            AccountStatus = ?, AccountOpeningDate = ?, LastTransactionDate = ?, InterestRate = ?,
            MaturityDate = ?, BeneficiaryInfo = ?, AccountHolderName = ?, BranchLocation = ?,
            Currency = ?, Documentation = ?, Notes = ?
        WHERE AssetId = ?
        """
        
        # Prepare parameters
        params = (
            data['DeceasedId'],
            data['InstitutionId'],
            data['AssetType'],
            data.get('Identifier'),
            data.get('EstimatedValue'),
            data.get('AccountStatus'),
            data.get('AccountOpeningDate'),
            data.get('LastTransactionDate'),
            data.get('InterestRate'),
            data.get('MaturityDate'),
            data.get('BeneficiaryInfo'),
            data.get('AccountHolderName'),
            data.get('BranchLocation'),
            data.get('Currency', 'USD'),
            data.get('Documentation'),
            data.get('Notes'),
            asset_id
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to update asset record: {e}")
    
    def delete(self, asset_id: int) -> bool:
        """
        Delete an asset record.
        
        Note: This will cascade delete associated claims.
        
        Args:
            asset_id: The ID of the asset record to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "DELETE FROM Assets WHERE AssetId = ?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (asset_id,))
                return cursor.rowcount > 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to delete asset record: {e}")
    
    def count(self) -> int:
        """
        Get the total count of asset records.
        
        Returns:
            int: Total number of asset records
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT COUNT(*) FROM Assets"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to count asset records: {e}")
    
    def get_total_value(self) -> Decimal:
        """
        Get the total estimated value of all assets.
        
        Returns:
            Decimal: Total estimated value of all assets
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = "SELECT SUM(EstimatedValue) FROM Assets WHERE EstimatedValue IS NOT NULL"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                return Decimal(str(result[0])) if result[0] else Decimal('0')
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to calculate total asset value: {e}")
    
    def get_by_type(self, asset_type: str) -> List[Dict[str, Any]]:
        """
        Get all assets of a specific type.
        
        Args:
            asset_type: The type of asset to filter by
        
        Returns:
            List of dictionaries containing asset records of the specified type
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.CreatedAt,
               d.FirstName, d.LastName,
               i.Name as InstitutionName, i.Type as InstitutionType
        FROM Assets a
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        WHERE a.AssetType = ?
        ORDER BY d.LastName, d.FirstName
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (asset_type,))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'CreatedAt': row[6],
                        'DeceasedName': f"{row[7]} {row[8]}",
                        'InstitutionName': row[9],
                        'InstitutionType': row[10]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve assets by type: {e}")
    
    def get_with_claims_count(self) -> List[Dict[str, Any]]:
        """
        Get assets with claim counts.
        
        Returns:
            List of dictionaries containing assets with claim counts
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        query = """
        SELECT a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
               a.EstimatedValue, a.CreatedAt,
               d.FirstName, d.LastName,
               i.Name as InstitutionName, i.Type as InstitutionType,
               COUNT(c.ClaimId) as ClaimCount
        FROM Assets a
        INNER JOIN Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN Institutions i ON a.InstitutionId = i.InstitutionId
        LEFT JOIN Claims c ON a.AssetId = c.AssetId
        GROUP BY a.AssetId, a.DeceasedId, a.InstitutionId, a.AssetType, a.Identifier, 
                 a.EstimatedValue, a.CreatedAt, d.FirstName, d.LastName, i.Name, i.Type
        ORDER BY d.LastName, d.FirstName, a.AssetType
        """
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'AssetId': row[0],
                        'DeceasedId': row[1],
                        'InstitutionId': row[2],
                        'AssetType': row[3],
                        'Identifier': row[4],
                        'EstimatedValue': row[5],
                        'CreatedAt': row[6],
                        'DeceasedName': f"{row[7]} {row[8]}",
                        'InstitutionName': row[9],
                        'InstitutionType': row[10],
                        'ClaimCount': row[11]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve assets with claim count: {e}")
