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
from logging_config import get_logger

logger = get_logger(__name__)


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
    
    def create(self, data: Dict[str, Any], use_stored_procedure: bool = True) -> int:
        """
        Create a new claim record.
        
        Args:
            data: Dictionary containing claim record data
                - AssetId (required): ID of the asset being claimed
                - ClaimantId (required): ID of the claimant
                - Status (optional): Claim status (default: 'Pending')
                - Notes (optional): Additional notes
            use_stored_procedure: If True, use stored procedure with validation (default: True)
        
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
        
        # Use direct INSERT method (simpler and more reliable than stored procedure with output params)
        # The stored procedure can be used for validation, but direct INSERT is cleaner for Python
        query = """
        INSERT INTO Claims (AssetId, ClaimantId, Status, Notes)
        OUTPUT INSERTED.ClaimId
        VALUES (?, ?, ?, ?)
        """
        
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
                claim_id = result[0] if result else 0
                
                # Log audit entry if user is available
                if claim_id > 0:
                    from auth.session import get_current_user
                    user = get_current_user()
                    if user:
                        try:
                            audit_query = """
                            INSERT INTO AuditLog (UserId, Action, Entity, EntityId, Details)
                            VALUES (?, 'CREATE', 'Claim', ?, ?)
                            """
                            audit_params = (
                                user.get('UserId'),
                                str(claim_id),
                                f"Created claim for Asset {data['AssetId']} by Claimant {data['ClaimantId']}"
                            )
                            cursor.execute(audit_query, audit_params)
                            conn.commit()
                        except Exception:
                            pass  # Non-critical, continue even if audit fails
                
                return claim_id
                    
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to create claim record: {e}")
    
    def _create_with_stored_procedure(self, data: Dict[str, Any]) -> int:
        """
        Create claim using stored procedure with validation and transaction.
        
        This demonstrates the use of stored procedures for business logic.
        """
        from auth.session import get_current_user
        
        user = get_current_user()
        user_id = user.get('UserId') if user else None
        
        query = "EXEC dbo.SP_CreateClaimWithValidation @AssetId=?, @ClaimantId=?, @Status=?, @Notes=?, @UserId=?, @ClaimId=?, @ErrorMessage=?"
        
        # Output parameter for claim ID (integer) - must be SQL parameter object
        claim_id = pyodbc.SQL_INTEGER()
        error_message = pyodbc.SQL_VARCHAR(500)
        
        params = (
            data['AssetId'],
            data['ClaimantId'],
            data.get('Status', 'Pending'),
            data.get('Notes'),
            user_id,
            claim_id,
            error_message
        )
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if error_message.value:
                    raise ValueError(f"Stored procedure error: {error_message.value}")
                
                return claim_id.value if claim_id.value else 0
                
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
    
    def update_status(self, claim_id: int, status: str, notes: Optional[str] = None, use_stored_procedure: bool = False) -> tuple[bool, Optional[str]]:
        """
        Update only the status of a claim record.
        
        Args:
            claim_id: The ID of the claim record to update
            status: New status ('Pending', 'Verified', 'Settled')
            notes: Optional notes to add
            use_stored_procedure: If True, use stored procedure with transaction (default: False)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            
        Raises:
            pyodbc.Error: If database operation fails
        """
        logger.info(f"update_status called: claim_id={claim_id}, status={status}, use_stored_procedure={use_stored_procedure}")
        if use_stored_procedure:
            # Use stored procedure with transaction and audit logging
            logger.debug("Using stored procedure approach")
            return self._update_status_with_stored_procedure(claim_id, status, notes)
        else:
            # Direct UPDATE (legacy method)
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
                    return (cursor.rowcount > 0, None)
                    
            except pyodbc.Error as e:
                return (False, str(e))
    
    def _update_status_with_stored_procedure(self, claim_id: int, status: str, notes: Optional[str]) -> tuple[bool, Optional[str]]:
        """
        Update claim status using direct UPDATE statement with transaction and audit.
        
        This uses direct SQL instead of stored procedure to avoid pyodbc output parameter issues.
        """
        logger.info(f"Updating claim {claim_id} status to {status}")
        from auth.session import get_current_user
        
        user = get_current_user()
        user_id = user.get('UserId') if user else None
        logger.debug(f"User ID: {user_id}")
        
        # Use direct UPDATE instead of stored procedure to avoid output parameter issues
        # The stored procedure approach has issues with pyodbc output parameters
        timestamp_field = ""
        timestamp_value = None
        
        if status == 'Verified':
            timestamp_field = ", VerifiedAt = ?"
            timestamp_value = datetime.now()
            logger.debug(f"Setting VerifiedAt to {timestamp_value}")
        elif status == 'Settled':
            timestamp_field = ", SettledAt = ?"
            timestamp_value = datetime.now()
            logger.debug(f"Setting SettledAt to {timestamp_value}")
        
        query = f"""
        UPDATE Claims
        SET Status = ?, Notes = ?{timestamp_field}
        WHERE ClaimId = ?
        """
        
        params = [status, notes]
        if timestamp_value:
            params.append(timestamp_value)
        params.append(claim_id)
        
        logger.debug(f"Executing query: {query}")
        logger.debug(f"Parameters: {params}")
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                logger.debug(f"Rows affected: {rows_affected}")
                conn.commit()
                logger.info(f"Transaction committed successfully")
                
                # Audit logging
                if user_id:
                    from db.models_audit import AuditLogModel
                    audit = AuditLogModel()
                    audit.write(
                        user_id=user_id,
                        action="UPDATE",
                        entity="Claim",
                        entity_id=str(claim_id),
                        details=f"Updated claim status to {status}",
                        ip=None
                    )
                    logger.debug("Audit log entry created")
                
                success = rows_affected > 0
                logger.info(f"Update {'successful' if success else 'failed'} (rows affected: {rows_affected})")
                return (success, None)
                
        except pyodbc.Error as e:
            logger.error(f"Database error updating claim status: {e}", exc_info=True)
            return (False, str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating claim status: {e}", exc_info=True)
            return (False, str(e))
    
    def get_pending_claims(self, days_old: Optional[int] = None, institution_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get pending claims using stored procedure.
        
        Args:
            days_old: Filter by minimum days pending
            institution_id: Filter by institution
        
        Returns:
            List of pending claim records
        """
        query = "EXEC dbo.SP_GetPendingClaims @DaysOld=?, @InstitutionId=?"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (days_old, institution_id))
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    records.append({
                        'ClaimId': row[0],
                        'AssetId': row[1],
                        'ClaimantId': row[2],
                        'FiledAt': row[3],
                        'Notes': row[4],
                        'AssetType': row[5],
                        'EstimatedValue': row[6],
                        'DeceasedName': row[7],
                        'ClaimantName': row[8],
                        'InstitutionName': row[9],
                        'DaysPending': row[10]
                    })
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve pending claims: {e}")
    
    def get_all_using_view(self) -> List[Dict[str, Any]]:
        """
        Get all claims using the VW_Claims_Detailed view.
        
        This demonstrates the use of database views for simplified queries.
        
        Returns:
            List of detailed claim records from the view
        """
        query = "SELECT * FROM dbo.VW_Claims_Detailed ORDER BY FiledAt DESC"
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # Get column names
                columns = [column[0] for column in cursor.description]
                
                records = []
                for row in rows:
                    record = {}
                    for i, col in enumerate(columns):
                        record[col] = row[i]
                    records.append(record)
                
                return records
                
        except pyodbc.Error as e:
            raise pyodbc.Error(f"Failed to retrieve claims from view: {e}")
    
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
