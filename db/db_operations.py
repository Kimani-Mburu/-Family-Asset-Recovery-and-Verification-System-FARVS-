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
    # DECEASED OPERATIONS (Using Stored Procedures)
    # ========================================================================
    
    def create_deceased_with_validation(
        self,
        first_name: str,
        last_name: str,
        national_id: Optional[str] = None,
        middle_name: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
        date_of_death: Optional[datetime] = None,
        place_of_birth: Optional[str] = None,
        place_of_death: Optional[str] = None,
        address: Optional[str] = None,
        occupation: Optional[str] = None,
        marital_status: Optional[str] = None,
        next_of_kin: Optional[str] = None,
        death_certificate_number: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a deceased record using stored procedure with validation.
        
        Uses: SP_CreateDeceasedWithValidation
        - Validates required fields
        - Validates date logic
        - Checks for duplicate NationalId
        - Creates record in transaction
        - Logs audit automatically
        
        Args:
            first_name: First name (required)
            last_name: Last name (required)
            national_id: National ID (optional)
            middle_name: Middle name (optional)
            gender: Gender (optional)
            date_of_birth: Date of birth (optional)
            date_of_death: Date of death (optional)
            place_of_birth: Place of birth (optional)
            place_of_death: Place of death (optional)
            address: Address (optional)
            occupation: Occupation (optional)
            marital_status: Marital status (optional)
            next_of_kin: Next of kin (optional)
            death_certificate_number: Death certificate number (optional)
            notes: Notes (optional)
            user_id: ID of user creating the record (for audit)
        
        Returns:
            Tuple of (success: bool, deceased_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # For pyodbc, we need to use a different approach for output parameters
                # We'll use a workaround: call procedure and get results via SELECT
                # First, declare variables to hold output
                cursor.execute("""
                    DECLARE @DeceasedId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateDeceasedWithValidation
                        @NationalId = ?,
                        @FirstName = ?,
                        @MiddleName = ?,
                        @LastName = ?,
                        @Gender = ?,
                        @DateOfBirth = ?,
                        @DateOfDeath = ?,
                        @PlaceOfBirth = ?,
                        @PlaceOfDeath = ?,
                        @Address = ?,
                        @Occupation = ?,
                        @MaritalStatus = ?,
                        @NextOfKin = ?,
                        @DeathCertificateNumber = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @DeceasedId = @DeceasedId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @DeceasedId AS DeceasedId, @ErrorMessage AS ErrorMessage;
                """, (national_id, first_name, middle_name, last_name, gender,
                      date_of_birth, date_of_death, place_of_birth, place_of_death,
                      address, occupation, marital_status, next_of_kin,
                      death_certificate_number, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                deceased_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
                if error_msg:
                    logger.error(f"Failed to create deceased record: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"Deceased record created successfully: ID={deceased_id_value}")
                return (True, deceased_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating deceased record: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating deceased record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_deceased_record(
        self,
        deceased_id: int,
        first_name: str,
        last_name: str,
        national_id: Optional[str] = None,
        middle_name: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
        date_of_death: Optional[datetime] = None,
        place_of_birth: Optional[str] = None,
        place_of_death: Optional[str] = None,
        address: Optional[str] = None,
        occupation: Optional[str] = None,
        marital_status: Optional[str] = None,
        next_of_kin: Optional[str] = None,
        death_certificate_number: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update a deceased record using stored procedure.
        
        Uses: SP_UpdateDeceasedRecord
        - Validates record exists
        - Validates required fields
        - Validates date logic
        - Updates record in transaction
        - Logs audit automatically
        
        Args:
            deceased_id: ID of deceased record to update
            first_name: First name (required)
            last_name: Last name (required)
            ... (other fields same as create)
            user_id: ID of user making the update (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateDeceasedRecord
                        @DeceasedId = ?,
                        @NationalId = ?,
                        @FirstName = ?,
                        @MiddleName = ?,
                        @LastName = ?,
                        @Gender = ?,
                        @DateOfBirth = ?,
                        @DateOfDeath = ?,
                        @PlaceOfBirth = ?,
                        @PlaceOfDeath = ?,
                        @Address = ?,
                        @Occupation = ?,
                        @MaritalStatus = ?,
                        @NextOfKin = ?,
                        @DeathCertificateNumber = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (deceased_id, national_id, first_name, middle_name, last_name, gender,
                      date_of_birth, date_of_death, place_of_birth, place_of_death,
                      address, occupation, marital_status, next_of_kin,
                      death_certificate_number, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update deceased record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Deceased record {deceased_id} updated successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating deceased record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating deceased record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def delete_deceased_record(
        self,
        deceased_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a deceased record using stored procedure.
        
        Uses: SP_DeleteDeceasedRecord
        - Validates record exists
        - Checks for associated assets
        - Deletes record in transaction
        - Logs audit automatically
        
        Args:
            deceased_id: ID of deceased record to delete
            user_id: ID of user making the deletion (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_DeleteDeceasedRecord
                        @DeceasedId = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (deceased_id, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to delete deceased record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Deceased record {deceased_id} deleted successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error deleting deceased record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error deleting deceased record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def get_deceased_with_assets(
        self,
        deceased_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get deceased records with asset information using stored procedure.
        
        Uses: SP_GetDeceasedWithAssets
        - Returns all deceased with asset counts and total values
        - Or specific deceased if ID provided
        
        Args:
            deceased_id: Optional ID to get specific deceased (None = all)
        
        Returns:
            List of deceased records with asset information
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    EXEC dbo.SP_GetDeceasedWithAssets
                        @DeceasedId = ?
                """, (deceased_id,))
                
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
            logger.error(f"Database error getting deceased with assets: {e}")
            raise
    
    # ========================================================================
    # ASSETS OPERATIONS (Using Stored Procedures)
    # ========================================================================
    
    def create_asset_with_validation(
        self,
        deceased_id: int,
        institution_id: int,
        asset_type: str,
        identifier: Optional[str] = None,
        estimated_value: Optional[float] = None,
        # Bank Account fields
        account_status: Optional[str] = None,
        account_opening_date: Optional[datetime] = None,
        last_transaction_date: Optional[datetime] = None,
        interest_rate: Optional[float] = None,
        account_holder_name: Optional[str] = None,
        branch_location: Optional[str] = None,
        currency: str = 'USD',
        # Vehicle fields
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        vehicle_year: Optional[int] = None,
        vehicle_vin: Optional[str] = None,
        vehicle_registration: Optional[str] = None,
        vehicle_condition: Optional[str] = None,
        vehicle_mileage: Optional[int] = None,
        # Real Estate fields
        property_address: Optional[str] = None,
        property_type: Optional[str] = None,
        property_size: Optional[float] = None,
        property_condition: Optional[str] = None,
        property_tax_id: Optional[str] = None,
        # Investment fields
        investment_type: Optional[str] = None,
        maturity_date: Optional[datetime] = None,
        # Insurance Policy fields
        policy_number: Optional[str] = None,
        policy_type: Optional[str] = None,
        policy_start_date: Optional[datetime] = None,
        policy_end_date: Optional[datetime] = None,
        premium_amount: Optional[float] = None,
        # Common fields
        beneficiary_info: Optional[str] = None,
        documentation: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create an asset record using stored procedure with validation.
        
        Uses: SP_CreateAssetWithValidation
        - Validates required fields
        - Validates deceased and institution exist
        - Validates value constraints
        - Creates record in transaction
        - Logs audit automatically
        
        Args:
            deceased_id: ID of deceased person (required)
            institution_id: ID of institution (required)
            asset_type: Type of asset (required)
            identifier: Account/policy identifier (optional)
            estimated_value: Estimated value (optional)
            ... (other optional fields)
            user_id: ID of user creating the record (for audit)
        
        Returns:
            Tuple of (success: bool, asset_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @AssetId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateAssetWithValidation
                        @DeceasedId = ?,
                        @InstitutionId = ?,
                        @AssetType = ?,
                        @Identifier = ?,
                        @EstimatedValue = ?,
                        @AccountStatus = ?,
                        @AccountOpeningDate = ?,
                        @LastTransactionDate = ?,
                        @InterestRate = ?,
                        @AccountHolderName = ?,
                        @BranchLocation = ?,
                        @Currency = ?,
                        @VehicleMake = ?,
                        @VehicleModel = ?,
                        @VehicleYear = ?,
                        @VehicleVIN = ?,
                        @VehicleRegistration = ?,
                        @VehicleCondition = ?,
                        @VehicleMileage = ?,
                        @PropertyAddress = ?,
                        @PropertyType = ?,
                        @PropertySize = ?,
                        @PropertyCondition = ?,
                        @PropertyTaxId = ?,
                        @InvestmentType = ?,
                        @MaturityDate = ?,
                        @PolicyNumber = ?,
                        @PolicyType = ?,
                        @PolicyStartDate = ?,
                        @PolicyEndDate = ?,
                        @PremiumAmount = ?,
                        @BeneficiaryInfo = ?,
                        @Documentation = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @AssetId = @AssetId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @AssetId AS AssetId, @ErrorMessage AS ErrorMessage;
                """, (deceased_id, institution_id, asset_type, identifier, estimated_value,
                      account_status, account_opening_date, last_transaction_date, interest_rate,
                      account_holder_name, branch_location, currency,
                      vehicle_make, vehicle_model, vehicle_year, vehicle_vin, vehicle_registration,
                      vehicle_condition, vehicle_mileage,
                      property_address, property_type, property_size, property_condition, property_tax_id,
                      investment_type, maturity_date,
                      policy_number, policy_type, policy_start_date, policy_end_date, premium_amount,
                      beneficiary_info, documentation, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                asset_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
                if error_msg:
                    logger.error(f"Failed to create asset record: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"Asset record created successfully: ID={asset_id_value}")
                return (True, asset_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating asset record: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating asset record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_asset_record(
        self,
        asset_id: int,
        deceased_id: Optional[int] = None,
        institution_id: Optional[int] = None,
        asset_type: Optional[str] = None,
        identifier: Optional[str] = None,
        estimated_value: Optional[float] = None,
        # Bank Account fields
        account_status: Optional[str] = None,
        account_opening_date: Optional[datetime] = None,
        last_transaction_date: Optional[datetime] = None,
        interest_rate: Optional[float] = None,
        account_holder_name: Optional[str] = None,
        branch_location: Optional[str] = None,
        currency: Optional[str] = None,
        # Vehicle fields
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        vehicle_year: Optional[int] = None,
        vehicle_vin: Optional[str] = None,
        vehicle_registration: Optional[str] = None,
        vehicle_condition: Optional[str] = None,
        vehicle_mileage: Optional[int] = None,
        # Real Estate fields
        property_address: Optional[str] = None,
        property_type: Optional[str] = None,
        property_size: Optional[float] = None,
        property_condition: Optional[str] = None,
        property_tax_id: Optional[str] = None,
        # Investment fields
        investment_type: Optional[str] = None,
        maturity_date: Optional[datetime] = None,
        # Insurance Policy fields
        policy_number: Optional[str] = None,
        policy_type: Optional[str] = None,
        policy_start_date: Optional[datetime] = None,
        policy_end_date: Optional[datetime] = None,
        premium_amount: Optional[float] = None,
        # Common fields
        beneficiary_info: Optional[str] = None,
        documentation: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update an asset record using stored procedure.
        
        Uses: SP_UpdateAssetRecord
        - Validates record exists
        - Validates constraints
        - Updates only provided fields
        - Logs audit automatically
        
        Args:
            asset_id: ID of asset record to update
            ... (optional fields to update)
            user_id: ID of user making the update (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateAssetRecord
                        @AssetId = ?,
                        @DeceasedId = ?,
                        @InstitutionId = ?,
                        @AssetType = ?,
                        @Identifier = ?,
                        @EstimatedValue = ?,
                        @AccountStatus = ?,
                        @AccountOpeningDate = ?,
                        @LastTransactionDate = ?,
                        @InterestRate = ?,
                        @AccountHolderName = ?,
                        @BranchLocation = ?,
                        @Currency = ?,
                        @VehicleMake = ?,
                        @VehicleModel = ?,
                        @VehicleYear = ?,
                        @VehicleVIN = ?,
                        @VehicleRegistration = ?,
                        @VehicleCondition = ?,
                        @VehicleMileage = ?,
                        @PropertyAddress = ?,
                        @PropertyType = ?,
                        @PropertySize = ?,
                        @PropertyCondition = ?,
                        @PropertyTaxId = ?,
                        @InvestmentType = ?,
                        @MaturityDate = ?,
                        @PolicyNumber = ?,
                        @PolicyType = ?,
                        @PolicyStartDate = ?,
                        @PolicyEndDate = ?,
                        @PremiumAmount = ?,
                        @BeneficiaryInfo = ?,
                        @Documentation = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (asset_id, deceased_id, institution_id, asset_type, identifier, estimated_value,
                      account_status, account_opening_date, last_transaction_date, interest_rate,
                      account_holder_name, branch_location, currency,
                      vehicle_make, vehicle_model, vehicle_year, vehicle_vin, vehicle_registration,
                      vehicle_condition, vehicle_mileage,
                      property_address, property_type, property_size, property_condition, property_tax_id,
                      investment_type, maturity_date,
                      policy_number, policy_type, policy_start_date, policy_end_date, premium_amount,
                      beneficiary_info, documentation, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update asset record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Asset record {asset_id} updated successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating asset record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating asset record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def delete_asset_record(
        self,
        asset_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete an asset record using stored procedure.
        
        Uses: SP_DeleteAssetRecord
        - Validates record exists
        - Checks for associated claims
        - Deletes record in transaction
        - Logs audit automatically
        
        Args:
            asset_id: ID of asset record to delete
            user_id: ID of user making the deletion (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_DeleteAssetRecord
                        @AssetId = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (asset_id, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to delete asset record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Asset record {asset_id} deleted successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error deleting asset record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error deleting asset record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def get_assets_by_deceased(
        self,
        deceased_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get assets by deceased ID using stored procedure.
        
        Uses: SP_GetAssetsByDeceased
        - Returns all assets with details
        - Or assets for specific deceased if ID provided
        
        Args:
            deceased_id: Optional ID to filter by deceased (None = all)
        
        Returns:
            List of asset records with detailed information
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    EXEC dbo.SP_GetAssetsByDeceased
                        @DeceasedId = ?
                """, (deceased_id,))
                
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
            logger.error(f"Database error getting assets by deceased: {e}")
            raise
    
    # ========================================================================
    # CLAIMANTS OPERATIONS (Using Stored Procedures)
    # ========================================================================
    
    def create_claimant_with_validation(
        self,
        first_name: str,
        last_name: str,
        national_id: Optional[str] = None,
        middle_name: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
        gender: Optional[str] = None,
        relationship: Optional[str] = None,
        contact: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        occupation: Optional[str] = None,
        marital_status: Optional[str] = None,
        alternate_contact: Optional[str] = None,
        relationship_proof: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a claimant record using stored procedure with validation.
        
        Uses: SP_CreateClaimantWithValidation
        - Validates required fields
        - Checks for duplicate NationalId
        - Creates record in transaction
        - Logs audit automatically
        
        Args:
            first_name: First name (required)
            last_name: Last name (required)
            ... (other optional fields)
            user_id: ID of user creating the record (for audit)
        
        Returns:
            Tuple of (success: bool, claimant_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @ClaimantId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateClaimantWithValidation
                        @NationalId = ?,
                        @FirstName = ?,
                        @MiddleName = ?,
                        @LastName = ?,
                        @DateOfBirth = ?,
                        @Gender = ?,
                        @Relationship = ?,
                        @Contact = ?,
                        @Email = ?,
                        @Phone = ?,
                        @Address = ?,
                        @Occupation = ?,
                        @MaritalStatus = ?,
                        @AlternateContact = ?,
                        @RelationshipProof = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @ClaimantId = @ClaimantId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @ClaimantId AS ClaimantId, @ErrorMessage AS ErrorMessage;
                """, (national_id, first_name, middle_name, last_name, date_of_birth, gender,
                      relationship, contact, email, phone, address, occupation, marital_status,
                      alternate_contact, relationship_proof, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                claimant_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
                if error_msg:
                    logger.error(f"Failed to create claimant record: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"Claimant record created successfully: ID={claimant_id_value}")
                return (True, claimant_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating claimant record: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating claimant record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_claimant_record(
        self,
        claimant_id: int,
        national_id: Optional[str] = None,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
        gender: Optional[str] = None,
        relationship: Optional[str] = None,
        contact: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        occupation: Optional[str] = None,
        marital_status: Optional[str] = None,
        alternate_contact: Optional[str] = None,
        relationship_proof: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update a claimant record using stored procedure.
        
        Uses: SP_UpdateClaimantRecord
        - Validates record exists
        - Validates constraints
        - Updates only provided fields
        - Logs audit automatically
        
        Args:
            claimant_id: ID of claimant record to update
            ... (optional fields to update)
            user_id: ID of user making the update (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateClaimantRecord
                        @ClaimantId = ?,
                        @NationalId = ?,
                        @FirstName = ?,
                        @MiddleName = ?,
                        @LastName = ?,
                        @DateOfBirth = ?,
                        @Gender = ?,
                        @Relationship = ?,
                        @Contact = ?,
                        @Email = ?,
                        @Phone = ?,
                        @Address = ?,
                        @Occupation = ?,
                        @MaritalStatus = ?,
                        @AlternateContact = ?,
                        @RelationshipProof = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (claimant_id, national_id, first_name, middle_name, last_name, date_of_birth, gender,
                      relationship, contact, email, phone, address, occupation, marital_status,
                      alternate_contact, relationship_proof, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update claimant record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Claimant record {claimant_id} updated successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating claimant record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating claimant record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def delete_claimant_record(
        self,
        claimant_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a claimant record using stored procedure.
        
        Uses: SP_DeleteClaimantRecord
        - Validates record exists
        - Checks for associated claims
        - Deletes record in transaction
        - Logs audit automatically
        
        Args:
            claimant_id: ID of claimant record to delete
            user_id: ID of user making the deletion (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_DeleteClaimantRecord
                        @ClaimantId = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (claimant_id, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to delete claimant record: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Claimant record {claimant_id} deleted successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error deleting claimant record: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error deleting claimant record: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    # ========================================================================
    # INSTITUTIONS OPERATIONS (Using Stored Procedures)
    # ========================================================================
    
    def create_institution(
        self,
        name: str,
        institution_type: Optional[str] = None,
        contact: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create an institution record using stored procedure.
        
        Uses: SP_CreateInstitution
        - Validates required fields
        - Checks for duplicate name
        - Creates record in transaction
        - Logs audit automatically
        
        Args:
            name: Institution name (required)
            institution_type: Type of institution (optional)
            contact: Contact information (optional)
            address: Address (optional)
            phone: Phone number (optional)
            user_id: ID of user creating the record (for audit)
        
        Returns:
            Tuple of (success: bool, institution_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @InstitutionId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateInstitution
                        @Name = ?,
                        @Type = ?,
                        @Contact = ?,
                        @Address = ?,
                        @Phone = ?,
                        @UserId = ?,
                        @InstitutionId = @InstitutionId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @InstitutionId AS InstitutionId, @ErrorMessage AS ErrorMessage;
                """, (name, institution_type, contact, address, phone, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                institution_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
                if error_msg:
                    logger.error(f"Failed to create institution: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"Institution created successfully: ID={institution_id_value}")
                return (True, institution_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating institution: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating institution: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_institution(
        self,
        institution_id: int,
        name: Optional[str] = None,
        institution_type: Optional[str] = None,
        contact: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update an institution record using stored procedure.
        
        Uses: SP_UpdateInstitution
        - Validates record exists
        - Validates constraints
        - Updates only provided fields
        - Logs audit automatically
        
        Args:
            institution_id: ID of institution record to update
            ... (optional fields to update)
            user_id: ID of user making the update (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateInstitution
                        @InstitutionId = ?,
                        @Name = ?,
                        @Type = ?,
                        @Contact = ?,
                        @Address = ?,
                        @Phone = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (institution_id, name, institution_type, contact, address, phone, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update institution: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Institution {institution_id} updated successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating institution: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating institution: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def delete_institution(
        self,
        institution_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete an institution record using stored procedure.
        
        Uses: SP_DeleteInstitution
        - Validates record exists
        - Checks for associated assets
        - Deletes record in transaction
        - Logs audit automatically
        
        Args:
            institution_id: ID of institution record to delete
            user_id: ID of user making the deletion (for audit)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_DeleteInstitution
                        @InstitutionId = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (institution_id, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to delete institution: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"Institution {institution_id} deleted successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error deleting institution: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error deleting institution: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
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
                
                # Call stored procedure with output parameters
                cursor.execute("""
                    DECLARE @ClaimId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateClaimWithValidation
                        @AssetId = ?,
                        @ClaimantId = ?,
                        @Status = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @ClaimId = @ClaimId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @ClaimId AS ClaimId, @ErrorMessage AS ErrorMessage;
                """, (asset_id, claimant_id, status, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                # Get output parameter values
                claim_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
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
                
                # Call stored procedure with output parameters
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateClaimStatus
                        @ClaimId = ?,
                        @NewStatus = ?,
                        @Notes = ?,
                        @UserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (claim_id, new_status, notes, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                # Get output parameter values
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
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
        Get all claims with detailed information.
        
        Uses direct query (matches VW_Claims_Detailed view definition)
        - Pre-joined data from multiple tables
        - Returns detailed claim information
        
        Returns:
            List of detailed claim records
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Use direct query matching the view definition
                cursor.execute("""
                    SELECT 
                        c.ClaimId,
                        c.Status,
                        c.FiledAt,
                        c.VerifiedAt,
                        c.SettledAt,
                        c.Notes,
                        a.AssetId,
                        a.AssetType,
                        a.Identifier AS AssetIdentifier,
                        a.EstimatedValue,
                        d.DeceasedId,
                        d.FirstName + ' ' + d.LastName AS DeceasedName,
                        d.FirstName AS DeceasedFirstName,
                        d.LastName AS DeceasedLastName,
                        d.NationalId AS DeceasedNationalId,
                        cl.ClaimantId,
                        cl.FirstName + ' ' + cl.LastName AS ClaimantName,
                        cl.FirstName AS ClaimantFirstName,
                        cl.LastName AS ClaimantLastName,
                        cl.Relationship,
                        cl.Contact AS ClaimantContact,
                        i.InstitutionId,
                        i.Name AS InstitutionName,
                        i.Type AS InstitutionType,
                        DATEDIFF(DAY, c.FiledAt, GETDATE()) AS DaysPending
                    FROM dbo.Claims c
                    INNER JOIN dbo.Assets a ON c.AssetId = a.AssetId
                    INNER JOIN dbo.Deceased d ON a.DeceasedId = d.DeceasedId
                    INNER JOIN dbo.Claimants cl ON c.ClaimantId = cl.ClaimantId
                    INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId
                    ORDER BY c.FiledAt DESC
                """)
                
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
            logger.error(f"Database error getting claims: {e}")
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
                
                # Call stored procedure with output parameters
                cursor.execute("""
                    DECLARE @CreatedCount INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_BatchCreateAssets
                        @DeceasedId = ?,
                        @InstitutionId = ?,
                        @Assets = ?,
                        @UserId = ?,
                        @CreatedCount = @CreatedCount OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @CreatedCount AS CreatedCount, @ErrorMessage AS ErrorMessage;
                """, (deceased_id, institution_id, assets_str, user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                # Get output parameter values
                count = result[0] if result and result[0] else 0
                error_msg = result[1] if result and result[1] else None
                
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
        email: Optional[str] = None,
        create_sql_login: bool = True,
        sql_login_password: Optional[str] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a new user account - only allowed by Admin users.
        
        Uses: SP_CreateUserByAdmin
        - Validates creator is Admin (database-level security)
        - Validates username uniqueness
        - Validates role
        - Creates user in transaction
        - Automatically creates SQL Server login with appropriate permissions
        - Logs audit entry
        
        Args:
            username: Username for new account
            password_hash: Hashed password (bytes)
            role: User role ('Admin', 'Staff', 'Viewer')
            created_by_user_id: ID of admin user creating this account
            email: Optional email address
            create_sql_login: Whether to create SQL Server login (default: True)
            sql_login_password: Password for SQL Server login (defaults to temp password if not provided)
        
        Returns:
            Tuple of (success: bool, user_id: Optional[int], error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Call stored procedure with output parameters
                cursor.execute("""
                    DECLARE @NewUserId INT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_CreateUserByAdmin
                        @Username = ?,
                        @PasswordHash = ?,
                        @Role = ?,
                        @CreatedByUserId = ?,
                        @Email = ?,
                        @CreateSQLLogin = ?,
                        @SQLLoginPassword = ?,
                        @NewUserId = @NewUserId OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @NewUserId AS NewUserId, @ErrorMessage AS ErrorMessage;
                """, (username, password_hash, role, created_by_user_id, email, 
                      1 if create_sql_login else 0, sql_login_password))
                
                result = cursor.fetchone()
                conn.commit()
                
                # Get output parameter values
                user_id_value = result[0] if result and result[0] else None
                error_msg = result[1] if result and result[1] else None
                
                if error_msg:
                    logger.error(f"Failed to create user: {error_msg}")
                    return (False, None, error_msg)
                
                logger.info(f"User created successfully: ID={user_id_value}, Username={username}, SQL Login={'Yes' if create_sql_login else 'No'}")
                return (True, user_id_value, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error creating user: {e}"
            logger.error(error_msg)
            return (False, None, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error creating user: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, None, error_msg)
    
    def update_user_by_admin(
        self,
        user_id: int,
        updated_by_user_id: int,
        username: Optional[str] = None,
        password_hash: Optional[bytes] = None,
        role: Optional[str] = None,
        email: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update a user account - only allowed by Admin users.
        
        Uses: SP_UpdateUserByAdmin
        - Validates updater is Admin (database-level security)
        - Validates username uniqueness if changing
        - Validates role
        - Updates SQL Server login permissions if role changes
        - Logs audit entry
        
        Args:
            user_id: ID of user to update
            username: New username (optional)
            password_hash: New password hash (optional)
            role: New role (optional)
            email: New email (optional)
            updated_by_user_id: ID of admin user making the update
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_UpdateUserByAdmin
                        @UserId = ?,
                        @Username = ?,
                        @PasswordHash = ?,
                        @Role = ?,
                        @Email = ?,
                        @UpdatedByUserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (user_id, username, password_hash, role, email, updated_by_user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to update user: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"User {user_id} updated successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error updating user: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error updating user: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def delete_user_by_admin(
        self,
        user_id: int,
        deleted_by_user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a user account - only allowed by Admin users.
        
        Uses: SP_DeleteUserByAdmin
        - Validates deleter is Admin (database-level security)
        - Prevents self-deletion
        - Deletes SQL Server login if it exists
        - Logs audit entry
        
        Args:
            user_id: ID of user to delete
            deleted_by_user_id: ID of admin user making the deletion
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.SP_DeleteUserByAdmin
                        @UserId = ?,
                        @DeletedByUserId = ?,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
                """, (user_id, deleted_by_user_id))
                
                result = cursor.fetchone()
                conn.commit()
                
                success_value = bool(result[0]) if result and result[0] is not None else False
                error_msg = result[1] if result and result[1] else None
                
                if not success_value or error_msg:
                    logger.error(f"Failed to delete user: {error_msg}")
                    return (False, error_msg)
                
                logger.info(f"User {user_id} deleted successfully")
                return (True, None)
                
        except pyodbc.Error as e:
            error_msg = f"Database error deleting user: {e}"
            logger.error(error_msg)
            return (False, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error deleting user: {e}"
            logger.error(error_msg, exc_info=True)
            return (False, error_msg)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from the database.
        
        Uses: SP_GetAllUsers
        - Returns all users with their information
        
        Returns:
            List of user records
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("EXEC dbo.SP_GetAllUsers")
                
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
            logger.error(f"Database error getting users: {e}")
            raise


# Create a singleton instance for easy import
db_ops = DatabaseOperations()

