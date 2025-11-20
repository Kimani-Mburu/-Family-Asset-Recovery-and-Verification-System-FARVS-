"""
FARVS Database Operations - Database-Centric Architecture
==========================================================

This module provides a centralized, database-centric approach to all database operations.
All business logic, transactions, and data validation should be handled by stored procedures,
triggers, and views in the database. This Python module acts as a thin wrapper that calls
these database objects.

Key Principles:
1. All complex operations use stored procedures
2. Transactions and savepoints are managed in stored procedures
3. Triggers handle automatic operations (audit logging, status history, etc.)
4. Views provide simplified data access
5. Python code is minimal - just parameter passing and result handling

Benefits:
- Business logic centralized in database
- Better performance (compiled procedures)
- Automatic transaction management
- Consistent data validation
- Easier to maintain and update
"""

import pyodbc
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from db.db_connect import get_connection
from logging_config import get_logger

logger = get_logger(__name__)


class DatabaseOperations:
    """
    Centralized database operations class.
    
    This class provides methods to call stored procedures, execute transactions,
    and interact with views. All business logic is in the database.
    """
    
    def __init__(self):
        """Initialize the DatabaseOperations class."""
        pass
    
    # ========================================================================
    # CLAIMS OPERATIONS (Using Stored Procedures)
    # ========================================================================
    
    def create_claim_with_validation(
        self,
        asset_id: int,
        claimant_id: int,
        status: str = 'Pending',
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a claim using stored procedure with validation and transaction.
        
        Uses: SP_CreateClaimWithValidation
        - Validates asset exists
        - Validates claimant exists
        - Checks for duplicate claims
        - Creates claim in transaction
        - Logs audit automatically (via trigger)
        
        Args:
            asset_id: ID of the asset being claimed
            claimant_id: ID of the claimant
            status: Claim status (default: 'Pending')
            notes: Optional notes
            user_id: ID of user creating the claim (for audit)
        
        Returns:
            Tuple of (success: bool, claim_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure
                claim_id = cursor.var(int)  # Output parameter
                error_message = cursor.var(str, 500)  # Output parameter
                
                cursor.execute("""
                    EXEC dbo.SP_CreateClaimWithValidation
                        @AssetId = ?,
                        @ClaimantId = ?,
                        @Status = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @ClaimId = ? OUTPUT,
                        @ErrorMessage = ? OUTPUT
                """, (asset_id, claimant_id, status, notes, user_id, claim_id, error_message))
                
                conn.commit()
                
                # Get output parameter values
                claim_id_value = claim_id.value if claim_id.value else None
                error_msg = error_message.value if error_message.value else None
                
                if error_msg:
                    logger.error(f"Failed to create claim: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"Claim created successfully: ID={claim_id_value}")
                return (True, claim_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating claim: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating claim: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_claim_status(
        self,
        claim_id: int,
        new_status: str,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update claim status using stored procedure with transaction and audit.
        
        Uses: SP_UpdateClaimStatus
        - Validates claim exists
        - Updates status with appropriate timestamps
        - Records status history
        - Logs audit entry
        - All in a transaction
        
        Args:
            claim_id: ID of the claim to update
            new_status: New status ('Pending', 'Verified', 'Settled')
            notes: Optional notes
            user_id: ID of user making the update (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure
                success = cursor.var(int)  # Output parameter (BIT in SQL = int in Python)
                error_message = cursor.var(str, 500)  # Output parameter
                
                cursor.execute("""
                    EXEC dbo.SP_UpdateClaimStatus
                        @ClaimId = ?,
                        @NewStatus = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @Success = ? OUTPUT,
                        @ErrorMessage = ? OUTPUT
                """, (claim_id, new_status, notes, user_id, success, error_message))
                
                conn.commit()
                
                # Get output parameter values
                success_value = bool(success.value) if success.value is not None else False
                error_msg = error_message.value if error_message.value else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update claim status: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Claim {claim_id} status updated to {new_status}")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating claim status: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating claim status: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def get_pending_claims(
        self,
        days_old: Optional[int] = None,
        institution_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending claims using stored procedure.
        
        Uses: SP_GetPendingClaims
        - Filters by days pending
        - Filters by institution
        - Returns detailed information with joins
        
        Args:
            days_old: Minimum days pending (None = all)
            institution_id: Filter by institution (None = all)
        
        Returns:
            List of pending claim records
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure
                cursor.execute("""
                    EXEC dbo.SP_GetPendingClaims
                        @DaysOld = ?,
                        @InstitutionId = ?
                """, (days_old, institution_id))
                
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
            logger.error(f"Database error getting pending claims: {e}")
            raise
    
    # ========================================================================
    # VIEW-BASED OPERATIONS (Simplified Data Access)
    # ========================================================================
    
    def get_claims_detailed(self) -> List[Dict[str, Any]]:
        """
        Get all claims with detailed information using view.
        
        Uses: VW_Claims_Detailed
        - Pre-joined data from multiple tables
        - Simplified query
        - Better performance
        
        Returns:
            List of detailed claim records
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM dbo.VW_Claims_Detailed ORDER BY FiledAt DESC")
                
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                
                records = []
                for row in rows:
                    record = {}
                    for i, col in enumerate(columns):
                        record[col] = row[i]
                    records.append(record)
                
                return records
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting claims from view: {e}")
            raise
    
    def get_assets_summary(self) -> List[Dict[str, Any]]:
        """
        Get assets summary using view.
        
        Uses: VW_Assets_Summary
        - Aggregated asset information
        - Pre-calculated values
        
        Returns:
            List of asset summary records
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM dbo.VW_Assets_Summary ORDER BY TotalValue DESC")
                
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                
                records = []
                for row in rows:
                    record = {}
                    for i, col in enumerate(columns):
                        record[col] = row[i]
                    records.append(record)
                
                return records
                
        except pyodbc.Error as e:
            logger.error(f"Database error getting assets summary: {e}")
            raise
    
    # ========================================================================
    # TRANSACTION OPERATIONS (Manual Transaction Control)
    # ========================================================================
    
    def execute_transaction(
        self,
        operations: List[Tuple[str, tuple]],
        rollback_on_error: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute multiple operations in a single transaction.
        
        This allows you to execute multiple SQL statements atomically.
        If any operation fails, all are rolled back (unless rollback_on_error=False).
        
        Args:
            operations: List of (sql_query, parameters) tuples
            rollback_on_error: If True, rollback on any error (default: True)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        
        Example:
            operations = [
                ("INSERT INTO Assets (...) VALUES (...)", (param1, param2)),
                ("UPDATE Claims SET ... WHERE ...", (param1,)),
            ]
            success, error = db_ops.execute_transaction(operations)
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Begin transaction
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # Execute all operations
                    for sql, params in operations:
                        cursor.execute(sql, params)
                    
                    # Commit if all successful
                    conn.commit()
                    logger.info(f"Transaction committed: {len(operations)} operations")
                    return (True, None)
                    
                except Exception as e:
                    if rollback_on_error:
                        conn.rollback()
                        logger.error(f"Transaction rolled back: {e}")
                    error_msg = f"Transaction error: {e}"
                    return (False, error_msg)
                    
        except pyodbc.Error as e:
            error_msg = f"Database error in transaction: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in transaction: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def execute_with_savepoint(
        self,
        savepoint_name: str,
        operations: List[Tuple[str, tuple]],
        rollback_savepoint_on_error: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute operations with a savepoint for partial rollback.
        
        This allows you to rollback to a specific point without rolling back
        the entire transaction. Useful for batch operations where some can fail.
        
        Args:
            savepoint_name: Name for the savepoint
            operations: List of (sql_query, parameters) tuples
            rollback_savepoint_on_error: If True, rollback to savepoint on error
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Create savepoint
                    cursor.execute(f"SAVE TRANSACTION {savepoint_name}")
                    
                    # Execute all operations
                    for sql, params in operations:
                        cursor.execute(sql, params)
                    
                    logger.info(f"Savepoint '{savepoint_name}' operations completed: {len(operations)} operations")
                    return (True, None)
                    
                except Exception as e:
                    if rollback_savepoint_on_error:
                        cursor.execute(f"ROLLBACK TRANSACTION {savepoint_name}")
                        logger.warning(f"Rolled back to savepoint '{savepoint_name}': {e}")
                    error_msg = f"Savepoint error: {e}"
                    return (False, error_msg)
                    
        except pyodbc.Error as e:
            error_msg = f"Database error with savepoint: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error with savepoint: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    # ========================================================================
    # BATCH OPERATIONS (Using Stored Procedures with Savepoints)
    # ========================================================================
    
    def batch_create_assets(
        self,
        deceased_id: int,
        institution_id: int,
        assets_data: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> Tuple[bool, int, Optional[str]]:
        """
        Batch create multiple assets using stored procedure.
        
        Uses: SP_BatchCreateAssets
        - Creates multiple assets in a single transaction
        - Uses savepoints for each asset (partial success allowed)
        - Validates all assets before starting
        - Returns count of successfully created assets
        
        Args:
            deceased_id: ID of deceased person
            institution_id: ID of institution
            assets_data: List of asset dictionaries with keys: AssetType, Identifier, EstimatedValue
            user_id: ID of user creating assets (for audit)
        
        Returns:
            Tuple of (success: bool, created_count: int, error_message: Optional[str])
        """
        try:
            # Format assets data for stored procedure
            # Format: "Type1|Identifier1|Value1;Type2|Identifier2|Value2"
            assets_str = ";".join([
                f"{asset['AssetType']}|{asset.get('Identifier', '')}|{asset.get('EstimatedValue', 0)}"
                for asset in assets_data
            ])
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure
                created_count = cursor.var(int)  # Output parameter
                error_message = cursor.var(str, 500)  # Output parameter
                
                cursor.execute("""
                    EXEC dbo.SP_BatchCreateAssets
                        @DeceasedId = ?,
                        @InstitutionId = ?,
                        @Assets = ?,
                        @UserId = ?,
                        @CreatedCount = ? OUTPUT,
                        @ErrorMessage = ? OUTPUT
                """, (deceased_id, institution_id, assets_str, user_id, created_count, error_message))
                
                conn.commit()
                
                # Get output parameter values
                count = created_count.value if created_count.value else 0
                error_msg = error_message.value if error_message.value else None
                
                if error_msg:
                    logger.error(f"Batch create assets failed: {error_msg}")
                    return (False, count, error_msg)
                
                logger.info(f"Batch created {count} assets successfully")
                return (True, count, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error in batch create: {e}"
            logger.error(error_msg)
            return (False, 0, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in batch create: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, 0, error_msg)
    
    # ========================================================================
    # USER OPERATIONS (Using Stored Procedures with Security)
    # ========================================================================
    
    def create_user_by_admin(
        self,
        username: str,
        password_hash: bytes,
        role: str,
        created_by_user_id: int,
        email: Optional[str] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a new user account - only allowed by Admin users.
        
        Uses: SP_CreateUserByAdmin
        - Validates creator is Admin (database-level security)
        - Validates username uniqueness
        - Validates role
        - Creates user in transaction
        - Logs audit entry
        
        Args:
            username: Username for new account
            password_hash: Hashed password (bytes)
            role: User role ('Admin', 'Staff', 'Viewer')
            created_by_user_id: ID of admin user creating this account
            email: Optional email address
        
        Returns:
            Tuple of (success: bool, user_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure
                new_user_id = cursor.var(int)  # Output parameter
                error_message = cursor.var(str, 500)  # Output parameter
                
                cursor.execute("""
                    EXEC dbo.SP_CreateUserByAdmin
                        @Username = ?,
                        @PasswordHash = ?,
                        @Role = ?,
                        @CreatedByUserId = ?,
                        @Email = ?,
                        @NewUserId = ? OUTPUT,
                        @ErrorMessage = ? OUTPUT
                """, (username, password_hash, role, created_by_user_id, email, new_user_id, error_message))
                
                conn.commit()
                
                # Get output parameter values
                user_id_value = new_user_id.value if new_user_id.value else None
                error_msg = error_message.value if error_message.value else None
                
                if error_msg:
                    logger.error(f"Failed to create user: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"User created successfully: ID={user_id_value}, Username={username}")
                return (True, user_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating user: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating user: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)


# Create a singleton instance for easy import
db_ops = DatabaseOperations()

