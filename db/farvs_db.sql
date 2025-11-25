-- ============================================================================
-- FARVS Database Schema - Complete SQL Script
-- Family Asset Recovery and Verification System
-- ============================================================================
-- This script demonstrates:
-- 1. Database Normalization (1NF, 2NF, 3NF)
-- 2. Transactions (ACID properties)
-- 3. Stored Procedures
-- 4. Views
-- 5. Triggers
-- 6. Indexes and Constraints
-- 7. Sample Data with Transactions
-- ============================================================================

-- ============================================================================
-- SECTION 1: DATABASE CREATION
-- ============================================================================

IF DB_ID('FARVS') IS NULL
BEGIN
    CREATE DATABASE FARVS;
END
GO

USE FARVS;
GO

-- ============================================================================
-- SECTION 2: NORMALIZATION DOCUMENTATION
-- ============================================================================
/*
NORMALIZATION ANALYSIS:

1. FIRST NORMAL FORM (1NF):
   - Each table has a primary key (DeceasedId, InstitutionId, etc.)
   - All columns contain atomic values (no repeating groups)
   - Example: Deceased table - each row represents one deceased person
   
2. SECOND NORMAL FORM (2NF):
   - All tables are in 1NF
   - All non-key attributes are fully dependent on the primary key
   - Example: Assets table - EstimatedValue depends on AssetId, not on DeceasedId alone
   
3. THIRD NORMAL FORM (3NF):
   - All tables are in 2NF
   - No transitive dependencies (non-key attributes don't depend on other non-key attributes)
   - Example: Institutions table is separate from Assets to avoid storing institution
     details redundantly with each asset
     
NORMALIZATION BENEFITS:
- Eliminates data redundancy
- Prevents update anomalies
- Ensures data integrity
- Reduces storage requirements
- Simplifies maintenance
*/

-- ============================================================================
-- SECTION 3: DROP EXISTING OBJECTS (in reverse dependency order)
-- ============================================================================

-- Drop triggers first
IF OBJECT_ID('dbo.TR_Claims_StatusChange', 'TR') IS NOT NULL DROP TRIGGER dbo.TR_Claims_StatusChange;
IF OBJECT_ID('dbo.TR_Assets_AfterInsert', 'TR') IS NOT NULL DROP TRIGGER dbo.TR_Assets_AfterInsert;
IF OBJECT_ID('dbo.TR_Deceased_AfterUpdate', 'TR') IS NOT NULL DROP TRIGGER dbo.TR_Deceased_AfterUpdate;
GO

-- Drop views
IF OBJECT_ID('dbo.VW_Claims_Detailed', 'V') IS NOT NULL DROP VIEW dbo.VW_Claims_Detailed;
IF OBJECT_ID('dbo.VW_Assets_Summary', 'V') IS NOT NULL DROP VIEW dbo.VW_Assets_Summary;
IF OBJECT_ID('dbo.VW_Deceased_WithAssets', 'V') IS NOT NULL DROP VIEW dbo.VW_Deceased_WithAssets;
IF OBJECT_ID('dbo.VW_Claimants_WithClaims', 'V') IS NOT NULL DROP VIEW dbo.VW_Claimants_WithClaims;
IF OBJECT_ID('dbo.VW_System_Statistics', 'V') IS NOT NULL DROP VIEW dbo.VW_System_Statistics;
GO

-- Drop stored procedures (in reverse dependency order)
IF OBJECT_ID('dbo.SP_GetAllUsers', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_GetAllUsers;
IF OBJECT_ID('dbo.SP_DeleteUserByAdmin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteUserByAdmin;
IF OBJECT_ID('dbo.SP_UpdateUserByAdmin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateUserByAdmin;
IF OBJECT_ID('dbo.SP_DropSQLServerLogin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DropSQLServerLogin;
IF OBJECT_ID('dbo.SP_UpdateSQLServerLoginPermissions', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateSQLServerLoginPermissions;
IF OBJECT_ID('dbo.SP_CreateSQLServerLogin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateSQLServerLogin;
IF OBJECT_ID('dbo.SP_CreateUserByAdmin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateUserByAdmin;
IF OBJECT_ID('dbo.SP_BatchCreateAssets', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_BatchCreateAssets;
IF OBJECT_ID('dbo.SP_GetPendingClaims', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_GetPendingClaims;
IF OBJECT_ID('dbo.SP_UpdateClaimStatus', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateClaimStatus;
IF OBJECT_ID('dbo.SP_CreateClaimWithValidation', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateClaimWithValidation;
-- New stored procedures for migration
IF OBJECT_ID('dbo.SP_CreateDeceasedWithValidation', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateDeceasedWithValidation;
IF OBJECT_ID('dbo.SP_UpdateDeceasedRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateDeceasedRecord;
IF OBJECT_ID('dbo.SP_DeleteDeceasedRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteDeceasedRecord;
IF OBJECT_ID('dbo.SP_GetDeceasedWithAssets', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_GetDeceasedWithAssets;
IF OBJECT_ID('dbo.SP_CreateAssetWithValidation', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateAssetWithValidation;
IF OBJECT_ID('dbo.SP_UpdateAssetRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateAssetRecord;
IF OBJECT_ID('dbo.SP_DeleteAssetRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteAssetRecord;
IF OBJECT_ID('dbo.SP_GetAssetsByDeceased', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_GetAssetsByDeceased;
IF OBJECT_ID('dbo.SP_CreateClaimantWithValidation', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateClaimantWithValidation;
IF OBJECT_ID('dbo.SP_UpdateClaimantRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateClaimantRecord;
IF OBJECT_ID('dbo.SP_DeleteClaimantRecord', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteClaimantRecord;
IF OBJECT_ID('dbo.SP_CreateInstitution', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateInstitution;
IF OBJECT_ID('dbo.SP_UpdateInstitution', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateInstitution;
IF OBJECT_ID('dbo.SP_DeleteInstitution', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteInstitution;
GO

-- Drop tables (reverse dependency order)
IF OBJECT_ID('dbo.Attachments', 'U') IS NOT NULL DROP TABLE dbo.Attachments;
IF OBJECT_ID('dbo.Notes', 'U') IS NOT NULL DROP TABLE dbo.Notes;
IF OBJECT_ID('dbo.Tasks', 'U') IS NOT NULL DROP TABLE dbo.Tasks;
IF OBJECT_ID('dbo.Cases', 'U') IS NOT NULL DROP TABLE dbo.Cases;
IF OBJECT_ID('dbo.StatusHistory', 'U') IS NOT NULL DROP TABLE dbo.StatusHistory;
IF OBJECT_ID('dbo.AssetValuations', 'U') IS NOT NULL DROP TABLE dbo.AssetValuations;
IF OBJECT_ID('dbo.AssetTypes', 'U') IS NOT NULL DROP TABLE dbo.AssetTypes;
-- Drop asset detail tables
IF OBJECT_ID('dbo.AssetInsurancePolicy', 'U') IS NOT NULL DROP TABLE dbo.AssetInsurancePolicy;
IF OBJECT_ID('dbo.AssetInvestment', 'U') IS NOT NULL DROP TABLE dbo.AssetInvestment;
IF OBJECT_ID('dbo.AssetRealEstate', 'U') IS NOT NULL DROP TABLE dbo.AssetRealEstate;
IF OBJECT_ID('dbo.AssetVehicle', 'U') IS NOT NULL DROP TABLE dbo.AssetVehicle;
IF OBJECT_ID('dbo.AssetBankAccount', 'U') IS NOT NULL DROP TABLE dbo.AssetBankAccount;
IF OBJECT_ID('dbo.AuditLog', 'U') IS NOT NULL DROP TABLE dbo.AuditLog;
IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
IF OBJECT_ID('dbo.Claims', 'U') IS NOT NULL DROP TABLE dbo.Claims;
IF OBJECT_ID('dbo.Assets', 'U') IS NOT NULL DROP TABLE dbo.Assets;
IF OBJECT_ID('dbo.Claimants', 'U') IS NOT NULL DROP TABLE dbo.Claimants;
IF OBJECT_ID('dbo.Institutions', 'U') IS NOT NULL DROP TABLE dbo.Institutions;
IF OBJECT_ID('dbo.Deceased', 'U') IS NOT NULL DROP TABLE dbo.Deceased;
GO

-- ============================================================================
-- SECTION 4: TABLE CREATION (Normalized Schema)
-- ============================================================================

-- Core Tables (1NF, 2NF, 3NF compliant)

-- Deceased Persons Table
CREATE TABLE dbo.Deceased (
    DeceasedId INT IDENTITY(1,1) PRIMARY KEY,
    NationalId VARCHAR(20) NULL,
    FirstName NVARCHAR(100) NOT NULL,
    MiddleName NVARCHAR(100) NULL,
    LastName NVARCHAR(100) NOT NULL,
    Gender NVARCHAR(20) NULL,
    DateOfBirth DATE NULL,
    DateOfDeath DATE NULL,
    PlaceOfBirth NVARCHAR(200) NULL,
    PlaceOfDeath NVARCHAR(200) NULL,
    Address NVARCHAR(500) NULL,
    Occupation NVARCHAR(100) NULL,
    MaritalStatus NVARCHAR(50) NULL,
    NextOfKin NVARCHAR(200) NULL,
    DeathCertificateNumber NVARCHAR(100) NULL,
    Notes NVARCHAR(1000) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    -- Check constraint for data validation
    CONSTRAINT CK_Deceased_Dates CHECK (DateOfDeath IS NULL OR DateOfBirth IS NULL OR DateOfDeath >= DateOfBirth)
);

-- Unique index for NationalId (normalization: prevents duplicate persons)
CREATE UNIQUE INDEX IX_Deceased_NationalId ON dbo.Deceased(NationalId) WHERE NationalId IS NOT NULL;

-- Index for search performance
CREATE INDEX IX_Deceased_Name ON dbo.Deceased(LastName, FirstName);

-- Institutions Table (3NF: separate table to avoid redundancy)
CREATE TABLE dbo.Institutions (
    InstitutionId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(200) NOT NULL,
    Type NVARCHAR(100) NULL,
    Contact NVARCHAR(200) NULL,
    Address NVARCHAR(500) NULL,
    Phone NVARCHAR(50) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Index for institution search
CREATE INDEX IX_Institutions_Name ON dbo.Institutions(Name);
CREATE INDEX IX_Institutions_Type ON dbo.Institutions(Type);

-- Assets Table (2NF: fully dependent on AssetId, references Deceased and Institution)
CREATE TABLE dbo.Assets (
    AssetId INT IDENTITY(1,1) PRIMARY KEY,
    DeceasedId INT NOT NULL,
    InstitutionId INT NOT NULL,
    AssetType NVARCHAR(100) NOT NULL,
    Identifier NVARCHAR(200) NULL,
    EstimatedValue DECIMAL(18,2) NULL,
    AccountStatus NVARCHAR(50) NULL,
    AccountOpeningDate DATE NULL,
    LastTransactionDate DATE NULL,
    InterestRate DECIMAL(5,2) NULL,
    MaturityDate DATE NULL,
    BeneficiaryInfo NVARCHAR(500) NULL,
    AccountHolderName NVARCHAR(200) NULL,
    BranchLocation NVARCHAR(200) NULL,
    Currency NVARCHAR(10) NULL DEFAULT 'USD',
    Documentation NVARCHAR(500) NULL,
    Notes NVARCHAR(1000) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    -- Foreign key constraints (referential integrity)
    CONSTRAINT FK_Assets_Deceased FOREIGN KEY (DeceasedId) REFERENCES dbo.Deceased(DeceasedId) ON DELETE CASCADE,
    CONSTRAINT FK_Assets_Institution FOREIGN KEY (InstitutionId) REFERENCES dbo.Institutions(InstitutionId),
    -- Check constraint for value validation
    CONSTRAINT CK_Assets_Value CHECK (EstimatedValue IS NULL OR EstimatedValue >= 0),
    -- Check constraint for interest rate
    CONSTRAINT CK_Assets_InterestRate CHECK (InterestRate IS NULL OR (InterestRate >= 0 AND InterestRate <= 100))
);

-- Indexes for performance
CREATE INDEX IX_Assets_DeceasedId ON dbo.Assets(DeceasedId);
CREATE INDEX IX_Assets_InstitutionId ON dbo.Assets(InstitutionId);
CREATE INDEX IX_Assets_Type ON dbo.Assets(AssetType);

-- Asset Detail Tables (Normalized: Type-specific attributes in separate tables)
-- This follows 3NF: Each asset type has its own detail table to avoid NULL columns

-- Bank Account Details
CREATE TABLE dbo.AssetBankAccount (
    AssetId INT PRIMARY KEY,
    AccountStatus NVARCHAR(50) NULL,
    AccountOpeningDate DATE NULL,
    LastTransactionDate DATE NULL,
    InterestRate DECIMAL(5,2) NULL,
    AccountHolderName NVARCHAR(200) NULL,
    BranchLocation NVARCHAR(200) NULL,
    Currency NVARCHAR(10) NULL DEFAULT 'USD',
    CONSTRAINT FK_AssetBankAccount_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetBankAccount_InterestRate CHECK (InterestRate IS NULL OR (InterestRate >= 0 AND InterestRate <= 100))
);

-- Vehicle Details
CREATE TABLE dbo.AssetVehicle (
    AssetId INT PRIMARY KEY,
    VehicleMake NVARCHAR(100) NULL,
    VehicleModel NVARCHAR(100) NULL,
    VehicleYear INT NULL,
    VehicleVIN NVARCHAR(50) NULL,
    VehicleRegistration NVARCHAR(100) NULL,
    VehicleCondition NVARCHAR(50) NULL,
    VehicleMileage INT NULL,
    CONSTRAINT FK_AssetVehicle_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetVehicle_Year CHECK (VehicleYear IS NULL OR (VehicleYear >= 1900 AND VehicleYear <= 2100)),
    CONSTRAINT CK_AssetVehicle_Mileage CHECK (VehicleMileage IS NULL OR VehicleMileage >= 0)
);

-- Real Estate Details
CREATE TABLE dbo.AssetRealEstate (
    AssetId INT PRIMARY KEY,
    PropertyAddress NVARCHAR(500) NULL,
    PropertyType NVARCHAR(100) NULL,
    PropertySize DECIMAL(10,2) NULL, -- Square feet
    PropertyCondition NVARCHAR(50) NULL,
    PropertyTaxId NVARCHAR(100) NULL,
    CONSTRAINT FK_AssetRealEstate_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetRealEstate_Size CHECK (PropertySize IS NULL OR PropertySize >= 0)
);

-- Investment Details
CREATE TABLE dbo.AssetInvestment (
    AssetId INT PRIMARY KEY,
    AccountStatus NVARCHAR(50) NULL,
    AccountOpeningDate DATE NULL,
    MaturityDate DATE NULL,
    InterestRate DECIMAL(5,2) NULL,
    Currency NVARCHAR(10) NULL DEFAULT 'USD',
    InvestmentType NVARCHAR(100) NULL, -- Stocks, Bonds, Mutual Funds, etc.
    CONSTRAINT FK_AssetInvestment_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetInvestment_InterestRate CHECK (InterestRate IS NULL OR (InterestRate >= 0 AND InterestRate <= 100))
);

-- Insurance Policy Details
CREATE TABLE dbo.AssetInsurancePolicy (
    AssetId INT PRIMARY KEY,
    PolicyNumber NVARCHAR(100) NULL,
    PolicyType NVARCHAR(100) NULL, -- Life, Health, Property, Auto, etc.
    PolicyStartDate DATE NULL,
    PolicyEndDate DATE NULL,
    PremiumAmount DECIMAL(18,2) NULL,
    CONSTRAINT FK_AssetInsurancePolicy_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetInsurancePolicy_Premium CHECK (PremiumAmount IS NULL OR PremiumAmount >= 0),
    CONSTRAINT CK_AssetInsurancePolicy_Dates CHECK (PolicyEndDate IS NULL OR PolicyStartDate IS NULL OR PolicyEndDate >= PolicyStartDate)
);

-- Indexes for asset detail tables
CREATE INDEX IX_AssetBankAccount_AssetId ON dbo.AssetBankAccount(AssetId);
CREATE INDEX IX_AssetVehicle_AssetId ON dbo.AssetVehicle(AssetId);
CREATE INDEX IX_AssetRealEstate_AssetId ON dbo.AssetRealEstate(AssetId);
CREATE INDEX IX_AssetInvestment_AssetId ON dbo.AssetInvestment(AssetId);
CREATE INDEX IX_AssetInsurancePolicy_AssetId ON dbo.AssetInsurancePolicy(AssetId);

-- Claimants Table
CREATE TABLE dbo.Claimants (
    ClaimantId INT IDENTITY(1,1) PRIMARY KEY,
    NationalId VARCHAR(20) NULL,
    FirstName NVARCHAR(100) NOT NULL,
    MiddleName NVARCHAR(100) NULL,
    LastName NVARCHAR(100) NOT NULL,
    DateOfBirth DATE NULL,
    Gender NVARCHAR(20) NULL,
    Relationship NVARCHAR(100) NULL,
    Contact NVARCHAR(200) NULL,
    Email NVARCHAR(200) NULL,
    Phone NVARCHAR(50) NULL,
    Address NVARCHAR(500) NULL,
    Occupation NVARCHAR(100) NULL,
    MaritalStatus NVARCHAR(50) NULL,
    AlternateContact NVARCHAR(200) NULL,
    RelationshipProof NVARCHAR(500) NULL,
    Notes NVARCHAR(1000) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Unique index for NationalId
CREATE UNIQUE INDEX IX_Claimants_NationalId ON dbo.Claimants(NationalId) WHERE NationalId IS NOT NULL;
CREATE INDEX IX_Claimants_Name ON dbo.Claimants(LastName, FirstName);

-- Claims Table (3NF: links Assets to Claimants, status tracking)
CREATE TABLE dbo.Claims (
    ClaimId INT IDENTITY(1,1) PRIMARY KEY,
    AssetId INT NOT NULL,
    ClaimantId INT NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
    FiledAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    VerifiedAt DATETIME2 NULL,
    SettledAt DATETIME2 NULL,
    Notes NVARCHAR(1000) NULL,
    -- Foreign keys
    CONSTRAINT FK_Claims_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT FK_Claims_Claimant FOREIGN KEY (ClaimantId) REFERENCES dbo.Claimants(ClaimantId),
    -- Check constraint for status values
    CONSTRAINT CK_Claims_Status CHECK (Status IN ('Pending', 'Verified', 'Rejected', 'Settled', 'Closed')),
    -- Check constraint for dates
    CONSTRAINT CK_Claims_Dates CHECK (
        (VerifiedAt IS NULL OR VerifiedAt >= FiledAt) AND
        (SettledAt IS NULL OR SettledAt >= FiledAt)
    )
);

-- Indexes for claims
CREATE INDEX IX_Claims_AssetId ON dbo.Claims(AssetId);
CREATE INDEX IX_Claims_ClaimantId ON dbo.Claims(ClaimantId);
CREATE INDEX IX_Claims_Status ON dbo.Claims(Status);
CREATE INDEX IX_Claims_FiledAt ON dbo.Claims(FiledAt);

-- Users Table (for authentication and RBAC)
CREATE TABLE dbo.Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARBINARY(256) NOT NULL,
    Role NVARCHAR(50) NOT NULL DEFAULT 'Staff',
    Email NVARCHAR(200) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    LastLoginAt DATETIME2 NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT CK_Users_Role CHECK (Role IN ('Admin', 'Staff', 'Viewer'))
);

CREATE INDEX IX_Users_Username ON dbo.Users(Username);
CREATE INDEX IX_Users_Role ON dbo.Users(Role);

-- Audit Log Table (for tracking all changes)
CREATE TABLE dbo.AuditLog (
    AuditId BIGINT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NULL,
    Action NVARCHAR(100) NOT NULL,
    Entity NVARCHAR(100) NOT NULL,
    EntityId NVARCHAR(100) NULL,
    Details NVARCHAR(2000) NULL,
    IpAddress NVARCHAR(64) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_AuditLog_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_AuditLog_UserId ON dbo.AuditLog(UserId);
CREATE INDEX IX_AuditLog_Entity ON dbo.AuditLog(Entity, EntityId);
CREATE INDEX IX_AuditLog_CreatedAt ON dbo.AuditLog(CreatedAt);

-- Asset Types Taxonomy (normalized: separate table for asset types)
CREATE TABLE dbo.AssetTypes (
    AssetTypeId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL UNIQUE,
    ParentAssetTypeId INT NULL,
    Description NVARCHAR(500) NULL,
    CONSTRAINT FK_AssetTypes_Parent FOREIGN KEY (ParentAssetTypeId) REFERENCES dbo.AssetTypes(AssetTypeId)
);

-- Asset Valuations (time-series data, normalized)
CREATE TABLE dbo.AssetValuations (
    ValuationId BIGINT IDENTITY(1,1) PRIMARY KEY,
    AssetId INT NOT NULL,
    ValuationDate DATE NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    Source NVARCHAR(200) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_AssetValuations UNIQUE (AssetId, ValuationDate),
    CONSTRAINT FK_AssetValuations_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT CK_AssetValuations_Amount CHECK (Amount >= 0)
);

CREATE INDEX IX_AssetValuations_AssetId ON dbo.AssetValuations(AssetId);
CREATE INDEX IX_AssetValuations_Date ON dbo.AssetValuations(ValuationDate);

-- Status History (for audit trail)
CREATE TABLE dbo.StatusHistory (
    StatusHistoryId BIGINT IDENTITY(1,1) PRIMARY KEY,
    EntityType NVARCHAR(50) NOT NULL,
    EntityId INT NOT NULL,
    Status NVARCHAR(50) NOT NULL,
    ChangedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ChangedByUserId INT NULL,
    Notes NVARCHAR(1000) NULL,
    CONSTRAINT FK_StatusHistory_User FOREIGN KEY (ChangedByUserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_StatusHistory_Entity ON dbo.StatusHistory(EntityType, EntityId);

-- Cases Table (for case management)
CREATE TABLE dbo.Cases (
    CaseId INT IDENTITY(1,1) PRIMARY KEY,
    DeceasedId INT NULL,
    ClaimId INT NULL,
    Title NVARCHAR(200) NOT NULL,
    Description NVARCHAR(2000) NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Open',
    OpenedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ClosedAt DATETIME2 NULL,
    CreatedByUserId INT NULL,
    CONSTRAINT FK_Cases_Deceased FOREIGN KEY (DeceasedId) REFERENCES dbo.Deceased(DeceasedId),
    CONSTRAINT FK_Cases_Claim FOREIGN KEY (ClaimId) REFERENCES dbo.Claims(ClaimId),
    CONSTRAINT FK_Cases_User FOREIGN KEY (CreatedByUserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_Cases_Status ON dbo.Cases(Status);
CREATE INDEX IX_Cases_DeceasedId ON dbo.Cases(DeceasedId);

-- Tasks Table
CREATE TABLE dbo.Tasks (
    TaskId INT IDENTITY(1,1) PRIMARY KEY,
    CaseId INT NOT NULL,
    Title NVARCHAR(200) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
    DueDate DATE NULL,
    AssignedToUserId INT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Tasks_Case FOREIGN KEY (CaseId) REFERENCES dbo.Cases(CaseId) ON DELETE CASCADE,
    CONSTRAINT FK_Tasks_User FOREIGN KEY (AssignedToUserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_Tasks_CaseId ON dbo.Tasks(CaseId);
CREATE INDEX IX_Tasks_Status ON dbo.Tasks(Status);

-- Notes Table
CREATE TABLE dbo.Notes (
    NoteId BIGINT IDENTITY(1,1) PRIMARY KEY,
    CaseId INT NOT NULL,
    UserId INT NULL,
    Content NVARCHAR(2000) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Notes_Case FOREIGN KEY (CaseId) REFERENCES dbo.Cases(CaseId) ON DELETE CASCADE,
    CONSTRAINT FK_Notes_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_Notes_CaseId ON dbo.Notes(CaseId);

-- Attachments Table
CREATE TABLE dbo.Attachments (
    AttachmentId BIGINT IDENTITY(1,1) PRIMARY KEY,
    EntityType NVARCHAR(50) NOT NULL,
    EntityId INT NOT NULL,
    FileName NVARCHAR(260) NOT NULL,
    MimeType NVARCHAR(100) NULL,
    Location NVARCHAR(500) NOT NULL,
    UploadedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UploadedByUserId INT NULL,
    CONSTRAINT FK_Attachments_User FOREIGN KEY (UploadedByUserId) REFERENCES dbo.Users(UserId)
);

CREATE INDEX IX_Attachments_Entity ON dbo.Attachments(EntityType, EntityId);
GO

-- ============================================================================
-- SECTION 5: VIEWS (Virtual tables for complex queries)
-- ============================================================================

-- View: Detailed Claims Information
CREATE VIEW dbo.VW_Claims_Detailed
AS
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
    d.NationalId AS DeceasedNationalId,
    cl.ClaimantId,
    cl.FirstName + ' ' + cl.LastName AS ClaimantName,
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
INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId;
GO

-- View: Assets Summary
CREATE VIEW dbo.VW_Assets_Summary
AS
SELECT 
    a.AssetId,
    a.AssetType,
    a.Identifier,
    a.EstimatedValue,
    a.CreatedAt,
    d.DeceasedId,
    d.FirstName + ' ' + d.LastName AS DeceasedName,
    i.Name AS InstitutionName,
    i.Type AS InstitutionType,
    COUNT(cl.ClaimId) AS ClaimCount,
    SUM(CASE WHEN cl.Status = 'Settled' THEN 1 ELSE 0 END) AS SettledClaimCount
FROM dbo.Assets a
INNER JOIN dbo.Deceased d ON a.DeceasedId = d.DeceasedId
INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId
LEFT JOIN dbo.Claims cl ON a.AssetId = cl.AssetId
GROUP BY a.AssetId, a.AssetType, a.Identifier, a.EstimatedValue, a.CreatedAt,
         d.DeceasedId, d.FirstName, d.LastName, i.Name, i.Type;
GO

-- View: Deceased with Assets Count
CREATE VIEW dbo.VW_Deceased_WithAssets
AS
SELECT 
    d.DeceasedId,
    d.NationalId,
    d.FirstName,
    d.LastName,
    d.FirstName + ' ' + d.LastName AS FullName,
    d.DateOfBirth,
    d.DateOfDeath,
    d.CreatedAt,
    COUNT(a.AssetId) AS AssetCount,
    SUM(a.EstimatedValue) AS TotalAssetValue,
    COUNT(cl.ClaimId) AS ClaimCount
FROM dbo.Deceased d
LEFT JOIN dbo.Assets a ON d.DeceasedId = a.DeceasedId
LEFT JOIN dbo.Claims cl ON a.AssetId = cl.AssetId
GROUP BY d.DeceasedId, d.NationalId, d.FirstName, d.LastName, 
         d.DateOfBirth, d.DateOfDeath, d.CreatedAt;
GO

-- View: Claimants with Claims Count
CREATE VIEW dbo.VW_Claimants_WithClaims
AS
SELECT 
    cl.ClaimantId,
    cl.NationalId,
    cl.FirstName,
    cl.LastName,
    cl.FirstName + ' ' + cl.LastName AS FullName,
    cl.Relationship,
    cl.Contact,
    cl.Email,
    cl.CreatedAt,
    COUNT(c.ClaimId) AS TotalClaims,
    SUM(CASE WHEN c.Status = 'Pending' THEN 1 ELSE 0 END) AS PendingClaims,
    SUM(CASE WHEN c.Status = 'Settled' THEN 1 ELSE 0 END) AS SettledClaims
FROM dbo.Claimants cl
LEFT JOIN dbo.Claims c ON cl.ClaimantId = c.ClaimantId
GROUP BY cl.ClaimantId, cl.NationalId, cl.FirstName, cl.LastName, 
         cl.Relationship, cl.Contact, cl.Email, cl.CreatedAt;
GO

-- View: System Statistics
CREATE VIEW dbo.VW_System_Statistics
AS
SELECT 
    (SELECT COUNT(*) FROM dbo.Deceased) AS TotalDeceased,
    (SELECT COUNT(*) FROM dbo.Assets) AS TotalAssets,
    (SELECT COUNT(*) FROM dbo.Claims) AS TotalClaims,
    (SELECT COUNT(*) FROM dbo.Claims WHERE Status = 'Pending') AS PendingClaims,
    (SELECT COUNT(*) FROM dbo.Claims WHERE Status = 'Settled') AS SettledClaims,
    (SELECT COUNT(*) FROM dbo.Claimants) AS TotalClaimants,
    (SELECT COUNT(*) FROM dbo.Institutions) AS TotalInstitutions,
    (SELECT SUM(EstimatedValue) FROM dbo.Assets WHERE EstimatedValue IS NOT NULL) AS TotalAssetValue,
    (SELECT SUM(EstimatedValue) FROM dbo.Assets a 
     INNER JOIN dbo.Claims c ON a.AssetId = c.AssetId 
     WHERE c.Status = 'Settled' AND a.EstimatedValue IS NOT NULL) AS SettledAssetValue;
GO

-- ============================================================================
-- SECTION 6: STORED PROCEDURES (Encapsulated business logic)
-- ============================================================================

-- ============================================================================
-- DECEASED OPERATIONS
-- ============================================================================

-- Stored Procedure: Create Deceased Record with Validation
CREATE PROCEDURE dbo.SP_CreateDeceasedWithValidation
    @NationalId NVARCHAR(50) = NULL,
    @FirstName NVARCHAR(100),
    @MiddleName NVARCHAR(100) = NULL,
    @LastName NVARCHAR(100),
    @Gender NVARCHAR(20) = NULL,
    @DateOfBirth DATE = NULL,
    @DateOfDeath DATE = NULL,
    @PlaceOfBirth NVARCHAR(200) = NULL,
    @PlaceOfDeath NVARCHAR(200) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Occupation NVARCHAR(100) = NULL,
    @MaritalStatus NVARCHAR(50) = NULL,
    @NextOfKin NVARCHAR(200) = NULL,
    @DeathCertificateNumber NVARCHAR(100) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @DeceasedId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @DeceasedId = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validation: FirstName is required
        IF @FirstName IS NULL OR LEN(LTRIM(RTRIM(@FirstName))) = 0
        BEGIN
            SET @ErrorMessage = 'FirstName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: LastName is required
        IF @LastName IS NULL OR LEN(LTRIM(RTRIM(@LastName))) = 0
        BEGIN
            SET @ErrorMessage = 'LastName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: DateOfDeath should be after DateOfBirth
        IF @DateOfBirth IS NOT NULL AND @DateOfDeath IS NOT NULL
        BEGIN
            IF @DateOfDeath < @DateOfBirth
            BEGIN
                SET @ErrorMessage = 'DateOfDeath cannot be before DateOfBirth';
                ROLLBACK TRANSACTION;
                RETURN;
            END
        END
        
        -- Validation: Check for duplicate NationalId if provided
        IF @NationalId IS NOT NULL AND EXISTS (SELECT 1 FROM dbo.Deceased WHERE NationalId = @NationalId)
        BEGIN
            SET @ErrorMessage = 'NationalId already exists';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Insert record
        INSERT INTO dbo.Deceased (
            NationalId, FirstName, MiddleName, LastName, Gender,
            DateOfBirth, DateOfDeath, PlaceOfBirth, PlaceOfDeath,
            Address, Occupation, MaritalStatus, NextOfKin,
            DeathCertificateNumber, Notes
        )
        VALUES (
            @NationalId, @FirstName, @MiddleName, @LastName, @Gender,
            @DateOfBirth, @DateOfDeath, @PlaceOfBirth, @PlaceOfDeath,
            @Address, @Occupation, @MaritalStatus, @NextOfKin,
            @DeathCertificateNumber, @Notes
        );
        
        SET @DeceasedId = SCOPE_IDENTITY();
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Deceased', CAST(@DeceasedId AS NVARCHAR(100)),
                    'Created deceased record: ' + @FirstName + ' ' + @LastName);
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update Deceased Record
CREATE PROCEDURE dbo.SP_UpdateDeceasedRecord
    @DeceasedId INT,
    @NationalId NVARCHAR(50) = NULL,
    @FirstName NVARCHAR(100),
    @MiddleName NVARCHAR(100) = NULL,
    @LastName NVARCHAR(100),
    @Gender NVARCHAR(20) = NULL,
    @DateOfBirth DATE = NULL,
    @DateOfDeath DATE = NULL,
    @PlaceOfBirth NVARCHAR(200) = NULL,
    @PlaceOfDeath NVARCHAR(200) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Occupation NVARCHAR(100) = NULL,
    @MaritalStatus NVARCHAR(50) = NULL,
    @NextOfKin NVARCHAR(200) = NULL,
    @DeathCertificateNumber NVARCHAR(100) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: FirstName is required
        IF @FirstName IS NULL OR LEN(LTRIM(RTRIM(@FirstName))) = 0
        BEGIN
            SET @ErrorMessage = 'FirstName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: LastName is required
        IF @LastName IS NULL OR LEN(LTRIM(RTRIM(@LastName))) = 0
        BEGIN
            SET @ErrorMessage = 'LastName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: DateOfDeath should be after DateOfBirth
        IF @DateOfBirth IS NOT NULL AND @DateOfDeath IS NOT NULL
        BEGIN
            IF @DateOfDeath < @DateOfBirth
            BEGIN
                SET @ErrorMessage = 'DateOfDeath cannot be before DateOfBirth';
                ROLLBACK TRANSACTION;
                RETURN;
            END
        END
        
        -- Validation: Check for duplicate NationalId if provided and changed
        IF @NationalId IS NOT NULL 
           AND EXISTS (SELECT 1 FROM dbo.Deceased WHERE NationalId = @NationalId AND DeceasedId != @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'NationalId already exists for another record';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update record
        UPDATE dbo.Deceased
        SET NationalId = @NationalId,
            FirstName = @FirstName,
            MiddleName = @MiddleName,
            LastName = @LastName,
            Gender = @Gender,
            DateOfBirth = @DateOfBirth,
            DateOfDeath = @DateOfDeath,
            PlaceOfBirth = @PlaceOfBirth,
            PlaceOfDeath = @PlaceOfDeath,
            Address = @Address,
            Occupation = @Occupation,
            MaritalStatus = @MaritalStatus,
            NextOfKin = @NextOfKin,
            DeathCertificateNumber = @DeathCertificateNumber,
            Notes = @Notes
        WHERE DeceasedId = @DeceasedId;
        
        -- Audit logging (trigger will also log, but explicit for clarity)
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Deceased', CAST(@DeceasedId AS NVARCHAR(100)),
                    'Updated deceased record: ' + @FirstName + ' ' + @LastName);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete Deceased Record
CREATE PROCEDURE dbo.SP_DeleteDeceasedRecord
    @DeceasedId INT,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check for associated assets
        DECLARE @AssetCount INT;
        SELECT @AssetCount = COUNT(*) FROM dbo.Assets WHERE DeceasedId = @DeceasedId;
        
        IF @AssetCount > 0
        BEGIN
            SET @ErrorMessage = 'Cannot delete deceased record with ' + CAST(@AssetCount AS NVARCHAR(10)) + ' associated assets. Please delete associated assets first.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get name for audit
        DECLARE @FirstName NVARCHAR(100);
        DECLARE @LastName NVARCHAR(100);
        SELECT @FirstName = FirstName, @LastName = LastName
        FROM dbo.Deceased WHERE DeceasedId = @DeceasedId;
        
        -- Delete record
        DELETE FROM dbo.Deceased WHERE DeceasedId = @DeceasedId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'DELETE', 'Deceased', CAST(@DeceasedId AS NVARCHAR(100)),
                    'Deleted deceased record: ' + @FirstName + ' ' + @LastName);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Get Deceased with Assets
CREATE PROCEDURE dbo.SP_GetDeceasedWithAssets
    @DeceasedId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @DeceasedId IS NULL
    BEGIN
        -- Return all deceased with asset counts
        SELECT 
            d.DeceasedId,
            d.NationalId,
            d.FirstName,
            d.MiddleName,
            d.LastName,
            d.Gender,
            d.DateOfBirth,
            d.DateOfDeath,
            d.PlaceOfBirth,
            d.PlaceOfDeath,
            d.Address,
            d.Occupation,
            d.MaritalStatus,
            d.NextOfKin,
            d.DeathCertificateNumber,
            d.Notes,
            d.CreatedAt,
            COUNT(a.AssetId) AS AssetCount,
            ISNULL(SUM(a.EstimatedValue), 0) AS TotalAssetValue
        FROM dbo.Deceased d
        LEFT JOIN dbo.Assets a ON d.DeceasedId = a.DeceasedId
        GROUP BY 
            d.DeceasedId, d.NationalId, d.FirstName, d.MiddleName, d.LastName,
            d.Gender, d.DateOfBirth, d.DateOfDeath, d.PlaceOfBirth, d.PlaceOfDeath,
            d.Address, d.Occupation, d.MaritalStatus, d.NextOfKin,
            d.DeathCertificateNumber, d.Notes, d.CreatedAt
        ORDER BY d.LastName, d.FirstName;
    END
    ELSE
    BEGIN
        -- Return specific deceased with assets
        SELECT 
            d.DeceasedId,
            d.NationalId,
            d.FirstName,
            d.MiddleName,
            d.LastName,
            d.Gender,
            d.DateOfBirth,
            d.DateOfDeath,
            d.PlaceOfBirth,
            d.PlaceOfDeath,
            d.Address,
            d.Occupation,
            d.MaritalStatus,
            d.NextOfKin,
            d.DeathCertificateNumber,
            d.Notes,
            d.CreatedAt,
            COUNT(a.AssetId) AS AssetCount,
            ISNULL(SUM(a.EstimatedValue), 0) AS TotalAssetValue
        FROM dbo.Deceased d
        LEFT JOIN dbo.Assets a ON d.DeceasedId = a.DeceasedId
        WHERE d.DeceasedId = @DeceasedId
        GROUP BY 
            d.DeceasedId, d.NationalId, d.FirstName, d.MiddleName, d.LastName,
            d.Gender, d.DateOfBirth, d.DateOfDeath, d.PlaceOfBirth, d.PlaceOfDeath,
            d.Address, d.Occupation, d.MaritalStatus, d.NextOfKin,
            d.DeathCertificateNumber, d.Notes, d.CreatedAt;
    END
END;
GO

-- ============================================================================
-- CLAIMS OPERATIONS (Already exist, keeping for reference)
-- ============================================================================

-- Stored Procedure: Create Claim with Validation (demonstrates transaction)
CREATE PROCEDURE dbo.SP_CreateClaimWithValidation
    @AssetId INT,
    @ClaimantId INT,
    @Status NVARCHAR(50) = 'Pending',
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @ClaimId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @ClaimId = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate asset exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Assets WHERE AssetId = @AssetId)
        BEGIN
            SET @ErrorMessage = 'Asset not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validate claimant exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Claimants WHERE ClaimantId = @ClaimantId)
        BEGIN
            SET @ErrorMessage = 'Claimant not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check for duplicate claim
        IF EXISTS (SELECT 1 FROM dbo.Claims WHERE AssetId = @AssetId AND ClaimantId = @ClaimantId)
        BEGIN
            SET @ErrorMessage = 'Claim already exists for this asset and claimant';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Insert claim
        INSERT INTO dbo.Claims (AssetId, ClaimantId, Status, Notes)
        VALUES (@AssetId, @ClaimantId, @Status, @Notes);
        
        SET @ClaimId = SCOPE_IDENTITY();
        
        -- Log audit
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Claim', CAST(@ClaimId AS NVARCHAR(100)), 
                    'Created claim for Asset ' + CAST(@AssetId AS NVARCHAR(10)));
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update Claim Status (with transaction and audit)
CREATE PROCEDURE dbo.SP_UpdateClaimStatus
    @ClaimId INT,
    @NewStatus NVARCHAR(50),
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate claim exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Claims WHERE ClaimId = @ClaimId)
        BEGIN
            SET @ErrorMessage = 'Claim not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get old status
        DECLARE @OldStatus NVARCHAR(50);
        SELECT @OldStatus = Status FROM dbo.Claims WHERE ClaimId = @ClaimId;
        
        -- Update status with appropriate timestamp
        IF @NewStatus = 'Verified'
        BEGIN
            UPDATE dbo.Claims
            SET Status = @NewStatus,
                VerifiedAt = CASE WHEN VerifiedAt IS NULL THEN GETDATE() ELSE VerifiedAt END,
                Notes = ISNULL(@Notes, Notes)
            WHERE ClaimId = @ClaimId;
        END
        ELSE IF @NewStatus = 'Settled'
        BEGIN
            UPDATE dbo.Claims
            SET Status = @NewStatus,
                SettledAt = CASE WHEN SettledAt IS NULL THEN GETDATE() ELSE SettledAt END,
                Notes = ISNULL(@Notes, Notes)
            WHERE ClaimId = @ClaimId;
        END
        ELSE
        BEGIN
            UPDATE dbo.Claims
            SET Status = @NewStatus,
                Notes = ISNULL(@Notes, Notes)
            WHERE ClaimId = @ClaimId;
        END
        
        -- Record status history
        INSERT INTO dbo.StatusHistory (EntityType, EntityId, Status, ChangedByUserId, Notes)
        VALUES ('Claim', @ClaimId, @NewStatus, @UserId, 
                'Status changed from ' + @OldStatus + ' to ' + @NewStatus);
        
        -- Log audit
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Claim', CAST(@ClaimId AS NVARCHAR(100)),
                    'Status updated from ' + @OldStatus + ' to ' + @NewStatus);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete Deceased with Assets (cascade with transaction)
CREATE PROCEDURE dbo.SP_GetPendingClaims
    @DaysOld INT = NULL,
    @InstitutionId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        c.ClaimId,
        c.AssetId,
        c.ClaimantId,
        c.FiledAt,
        c.Notes,
        a.AssetType,
        a.EstimatedValue,
        d.FirstName + ' ' + d.LastName AS DeceasedName,
        cl.FirstName + ' ' + cl.LastName AS ClaimantName,
        i.Name AS InstitutionName,
        DATEDIFF(DAY, c.FiledAt, GETDATE()) AS DaysPending
    FROM dbo.Claims c
    INNER JOIN dbo.Assets a ON c.AssetId = a.AssetId
    INNER JOIN dbo.Deceased d ON a.DeceasedId = d.DeceasedId
    INNER JOIN dbo.Claimants cl ON c.ClaimantId = cl.ClaimantId
    INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId
    WHERE c.Status = 'Pending'
        AND (@DaysOld IS NULL OR DATEDIFF(DAY, c.FiledAt, GETDATE()) >= @DaysOld)
        AND (@InstitutionId IS NULL OR a.InstitutionId = @InstitutionId)
    ORDER BY c.FiledAt ASC;
END;
GO

-- Stored Procedure: Batch Create Assets (transaction for multiple inserts)
CREATE PROCEDURE dbo.SP_BatchCreateAssets
    @DeceasedId INT,
    @InstitutionId INT,
    @Assets NVARCHAR(MAX), -- JSON-like format: "Type1|Identifier1|Value1;Type2|Identifier2|Value2"
    @UserId INT = NULL,
    @CreatedCount INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @CreatedCount = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate deceased exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validate institution exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Institutions WHERE InstitutionId = @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Parse and insert assets with savepoints (allows partial success)
        DECLARE @AssetType NVARCHAR(100);
        DECLARE @Identifier NVARCHAR(200);
        DECLARE @Value DECIMAL(18,2);
        DECLARE @Pos INT;
        DECLARE @NextPos INT;
        DECLARE @Item NVARCHAR(500);
        DECLARE @Delimiter CHAR(1) = '|';
        DECLARE @Separator CHAR(1) = ';';
        DECLARE @FailedCount INT = 0;
        
        SET @Pos = 1;
        
        WHILE @Pos <= LEN(@Assets)
        BEGIN
            BEGIN TRY
                -- Create savepoint before each asset
                SAVE TRANSACTION Savepoint_BeforeAsset;
                
                SET @NextPos = CHARINDEX(@Separator, @Assets, @Pos);
                IF @NextPos = 0 SET @NextPos = LEN(@Assets) + 1;
                
                SET @Item = SUBSTRING(@Assets, @Pos, @NextPos - @Pos);
                
                -- Parse asset details (Type|Identifier|Value)
                SET @AssetType = SUBSTRING(@Item, 1, CHARINDEX(@Delimiter, @Item) - 1);
                SET @Item = SUBSTRING(@Item, CHARINDEX(@Delimiter, @Item) + 1, LEN(@Item));
                SET @Identifier = SUBSTRING(@Item, 1, CHARINDEX(@Delimiter, @Item) - 1);
                SET @Value = CAST(SUBSTRING(@Item, CHARINDEX(@Delimiter, @Item) + 1, LEN(@Item)) AS DECIMAL(18,2));
                
                -- Validate asset data
                IF @AssetType IS NULL OR LEN(@AssetType) = 0
                BEGIN
                    RAISERROR('Asset type is required', 16, 1);
                END
                
                IF @Value < 0
                BEGIN
                    RAISERROR('Asset value cannot be negative', 16, 1);
                END
                
                -- Insert asset
                INSERT INTO dbo.Assets (DeceasedId, InstitutionId, AssetType, Identifier, EstimatedValue)
                VALUES (@DeceasedId, @InstitutionId, @AssetType, @Identifier, @Value);
                
                SET @CreatedCount = @CreatedCount + 1;
            END TRY
            BEGIN CATCH
                -- Rollback only this asset, continue with next
                ROLLBACK TRANSACTION Savepoint_BeforeAsset;
                SET @FailedCount = @FailedCount + 1;
                -- Log error but continue processing
            END CATCH
            
            SET @Pos = @NextPos + 1;
        END
        
        -- Log audit
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Asset', CAST(@DeceasedId AS NVARCHAR(100)),
                    'Batch created ' + CAST(@CreatedCount AS NVARCHAR(10)) + ' assets');
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Bulk Verify Claims (with savepoints per claim)
CREATE PROCEDURE dbo.SP_CreateAssetWithValidation
    @DeceasedId INT,
    @InstitutionId INT,
    @AssetType NVARCHAR(100),
    @Identifier NVARCHAR(200) = NULL,
    @EstimatedValue DECIMAL(18,2) = NULL,
    -- Bank Account fields
    @AccountStatus NVARCHAR(50) = NULL,
    @AccountOpeningDate DATE = NULL,
    @LastTransactionDate DATE = NULL,
    @InterestRate DECIMAL(5,2) = NULL,
    @AccountHolderName NVARCHAR(200) = NULL,
    @BranchLocation NVARCHAR(200) = NULL,
    @Currency NVARCHAR(10) = 'USD',
    -- Vehicle fields
    @VehicleMake NVARCHAR(100) = NULL,
    @VehicleModel NVARCHAR(100) = NULL,
    @VehicleYear INT = NULL,
    @VehicleVIN NVARCHAR(50) = NULL,
    @VehicleRegistration NVARCHAR(100) = NULL,
    @VehicleCondition NVARCHAR(50) = NULL,
    @VehicleMileage INT = NULL,
    -- Real Estate fields
    @PropertyAddress NVARCHAR(500) = NULL,
    @PropertyType NVARCHAR(100) = NULL,
    @PropertySize DECIMAL(10,2) = NULL,
    @PropertyCondition NVARCHAR(50) = NULL,
    @PropertyTaxId NVARCHAR(100) = NULL,
    -- Investment fields
    @InvestmentType NVARCHAR(100) = NULL,
    @MaturityDate DATE = NULL,
    -- Insurance Policy fields
    @PolicyNumber NVARCHAR(100) = NULL,
    @PolicyType NVARCHAR(100) = NULL,
    @PolicyStartDate DATE = NULL,
    @PolicyEndDate DATE = NULL,
    @PremiumAmount DECIMAL(18,2) = NULL,
    -- Common fields
    @BeneficiaryInfo NVARCHAR(500) = NULL,
    @Documentation NVARCHAR(500) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @AssetId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @AssetId = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validation: DeceasedId is required
        IF @DeceasedId IS NULL
        BEGIN
            SET @ErrorMessage = 'DeceasedId is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: InstitutionId is required
        IF @InstitutionId IS NULL
        BEGIN
            SET @ErrorMessage = 'InstitutionId is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: AssetType is required
        IF @AssetType IS NULL OR LEN(LTRIM(RTRIM(@AssetType))) = 0
        BEGIN
            SET @ErrorMessage = 'AssetType is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Deceased exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Institution exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Institutions WHERE InstitutionId = @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: EstimatedValue must be non-negative
        IF @EstimatedValue IS NOT NULL AND @EstimatedValue < 0
        BEGIN
            SET @ErrorMessage = 'EstimatedValue cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: InterestRate must be between 0 and 100
        IF @InterestRate IS NOT NULL AND (@InterestRate < 0 OR @InterestRate > 100)
        BEGIN
            SET @ErrorMessage = 'InterestRate must be between 0 and 100';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: VehicleYear must be valid
        IF @VehicleYear IS NOT NULL AND (@VehicleYear < 1900 OR @VehicleYear > 2100)
        BEGIN
            SET @ErrorMessage = 'VehicleYear must be between 1900 and 2100';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: VehicleMileage must be non-negative
        IF @VehicleMileage IS NOT NULL AND @VehicleMileage < 0
        BEGIN
            SET @ErrorMessage = 'VehicleMileage cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: PropertySize must be non-negative
        IF @PropertySize IS NOT NULL AND @PropertySize < 0
        BEGIN
            SET @ErrorMessage = 'PropertySize cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: PremiumAmount must be non-negative
        IF @PremiumAmount IS NOT NULL AND @PremiumAmount < 0
        BEGIN
            SET @ErrorMessage = 'PremiumAmount cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Insert main asset record (only general fields)
        INSERT INTO dbo.Assets (
            DeceasedId, InstitutionId, AssetType, Identifier, EstimatedValue,
            Documentation, Notes
        )
        VALUES (
            @DeceasedId, @InstitutionId, @AssetType, @Identifier, @EstimatedValue,
            @Documentation, @Notes
        );
        
        SET @AssetId = SCOPE_IDENTITY();
        
        -- Insert into appropriate detail table based on asset type
        IF @AssetType = 'Bank Account'
        BEGIN
            INSERT INTO dbo.AssetBankAccount (
                AssetId, AccountStatus, AccountOpeningDate, LastTransactionDate,
                InterestRate, AccountHolderName, BranchLocation, Currency
            )
            VALUES (
                @AssetId, @AccountStatus, @AccountOpeningDate, @LastTransactionDate,
                @InterestRate, @AccountHolderName, @BranchLocation, @Currency
            );
        END
        ELSE IF @AssetType = 'Vehicle'
        BEGIN
            INSERT INTO dbo.AssetVehicle (
                AssetId, VehicleMake, VehicleModel, VehicleYear, VehicleVIN,
                VehicleRegistration, VehicleCondition, VehicleMileage
            )
            VALUES (
                @AssetId, @VehicleMake, @VehicleModel, @VehicleYear, @VehicleVIN,
                @VehicleRegistration, @VehicleCondition, @VehicleMileage
            );
        END
        ELSE IF @AssetType = 'Real Estate'
        BEGIN
            INSERT INTO dbo.AssetRealEstate (
                AssetId, PropertyAddress, PropertyType, PropertySize,
                PropertyCondition, PropertyTaxId
            )
            VALUES (
                @AssetId, @PropertyAddress, @PropertyType, @PropertySize,
                @PropertyCondition, @PropertyTaxId
            );
        END
        ELSE IF @AssetType = 'Investment'
        BEGIN
            INSERT INTO dbo.AssetInvestment (
                AssetId, AccountStatus, AccountOpeningDate, MaturityDate,
                InterestRate, Currency, InvestmentType
            )
            VALUES (
                @AssetId, @AccountStatus, @AccountOpeningDate, @MaturityDate,
                @InterestRate, @Currency, @InvestmentType
            );
        END
        ELSE IF @AssetType = 'Insurance Policy'
        BEGIN
            INSERT INTO dbo.AssetInsurancePolicy (
                AssetId, PolicyNumber, PolicyType, PolicyStartDate,
                PolicyEndDate, PremiumAmount
            )
            VALUES (
                @AssetId, @PolicyNumber, @PolicyType, @PolicyStartDate,
                @PolicyEndDate, @PremiumAmount
            );
        END
        
        -- Store BeneficiaryInfo in main Assets table if provided (common field)
        IF @BeneficiaryInfo IS NOT NULL
        BEGIN
            UPDATE dbo.Assets
            SET BeneficiaryInfo = @BeneficiaryInfo
            WHERE AssetId = @AssetId;
        END
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Asset', CAST(@AssetId AS NVARCHAR(100)),
                    'Created asset: ' + @AssetType + ' for Deceased ' + CAST(@DeceasedId AS NVARCHAR(10)));
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update Asset Record (Updated to handle detail tables)
CREATE PROCEDURE dbo.SP_UpdateAssetRecord
    @AssetId INT,
    @DeceasedId INT = NULL,
    @InstitutionId INT = NULL,
    @AssetType NVARCHAR(100) = NULL,
    @Identifier NVARCHAR(200) = NULL,
    @EstimatedValue DECIMAL(18,2) = NULL,
    -- Bank Account fields
    @AccountStatus NVARCHAR(50) = NULL,
    @AccountOpeningDate DATE = NULL,
    @LastTransactionDate DATE = NULL,
    @InterestRate DECIMAL(5,2) = NULL,
    @AccountHolderName NVARCHAR(200) = NULL,
    @BranchLocation NVARCHAR(200) = NULL,
    @Currency NVARCHAR(10) = NULL,
    -- Vehicle fields
    @VehicleMake NVARCHAR(100) = NULL,
    @VehicleModel NVARCHAR(100) = NULL,
    @VehicleYear INT = NULL,
    @VehicleVIN NVARCHAR(50) = NULL,
    @VehicleRegistration NVARCHAR(100) = NULL,
    @VehicleCondition NVARCHAR(50) = NULL,
    @VehicleMileage INT = NULL,
    -- Real Estate fields
    @PropertyAddress NVARCHAR(500) = NULL,
    @PropertyType NVARCHAR(100) = NULL,
    @PropertySize DECIMAL(10,2) = NULL,
    @PropertyCondition NVARCHAR(50) = NULL,
    @PropertyTaxId NVARCHAR(100) = NULL,
    -- Investment fields
    @InvestmentType NVARCHAR(100) = NULL,
    @MaturityDate DATE = NULL,
    -- Insurance Policy fields
    @PolicyNumber NVARCHAR(100) = NULL,
    @PolicyType NVARCHAR(100) = NULL,
    @PolicyStartDate DATE = NULL,
    @PolicyEndDate DATE = NULL,
    @PremiumAmount DECIMAL(18,2) = NULL,
    -- Common fields
    @BeneficiaryInfo NVARCHAR(500) = NULL,
    @Documentation NVARCHAR(500) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Assets WHERE AssetId = @AssetId)
        BEGIN
            SET @ErrorMessage = 'Asset record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get current asset type
        DECLARE @CurrentAssetType NVARCHAR(100);
        SELECT @CurrentAssetType = AssetType FROM dbo.Assets WHERE AssetId = @AssetId;
        
        -- If AssetType is being changed, we need to handle detail table migration
        DECLARE @NewAssetType NVARCHAR(100) = ISNULL(@AssetType, @CurrentAssetType);
        
        -- Validation: If DeceasedId is provided, it must exist
        IF @DeceasedId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: If InstitutionId is provided, it must exist
        IF @InstitutionId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dbo.Institutions WHERE InstitutionId = @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: EstimatedValue must be non-negative
        IF @EstimatedValue IS NOT NULL AND @EstimatedValue < 0
        BEGIN
            SET @ErrorMessage = 'EstimatedValue cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: InterestRate must be between 0 and 100
        IF @InterestRate IS NOT NULL AND (@InterestRate < 0 OR @InterestRate > 100)
        BEGIN
            SET @ErrorMessage = 'InterestRate must be between 0 and 100';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: VehicleYear must be valid
        IF @VehicleYear IS NOT NULL AND (@VehicleYear < 1900 OR @VehicleYear > 2100)
        BEGIN
            SET @ErrorMessage = 'VehicleYear must be between 1900 and 2100';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: VehicleMileage must be non-negative
        IF @VehicleMileage IS NOT NULL AND @VehicleMileage < 0
        BEGIN
            SET @ErrorMessage = 'VehicleMileage cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: PropertySize must be non-negative
        IF @PropertySize IS NOT NULL AND @PropertySize < 0
        BEGIN
            SET @ErrorMessage = 'PropertySize cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: PremiumAmount must be non-negative
        IF @PremiumAmount IS NOT NULL AND @PremiumAmount < 0
        BEGIN
            SET @ErrorMessage = 'PremiumAmount cannot be negative';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update main asset record (only general fields)
        UPDATE dbo.Assets
        SET DeceasedId = ISNULL(@DeceasedId, DeceasedId),
            InstitutionId = ISNULL(@InstitutionId, InstitutionId),
            AssetType = ISNULL(@AssetType, AssetType),
            Identifier = ISNULL(@Identifier, Identifier),
            EstimatedValue = ISNULL(@EstimatedValue, EstimatedValue),
            BeneficiaryInfo = ISNULL(@BeneficiaryInfo, BeneficiaryInfo),
            Documentation = ISNULL(@Documentation, Documentation),
            Notes = ISNULL(@Notes, Notes)
        WHERE AssetId = @AssetId;
        
        -- Update detail table based on asset type
        -- If asset type changed, delete old detail record and create new one
        IF @CurrentAssetType != @NewAssetType
        BEGIN
            -- Delete old detail record
            IF @CurrentAssetType = 'Bank Account'
                DELETE FROM dbo.AssetBankAccount WHERE AssetId = @AssetId;
            ELSE IF @CurrentAssetType = 'Vehicle'
                DELETE FROM dbo.AssetVehicle WHERE AssetId = @AssetId;
            ELSE IF @CurrentAssetType = 'Real Estate'
                DELETE FROM dbo.AssetRealEstate WHERE AssetId = @AssetId;
            ELSE IF @CurrentAssetType = 'Investment'
                DELETE FROM dbo.AssetInvestment WHERE AssetId = @AssetId;
            ELSE IF @CurrentAssetType = 'Insurance Policy'
                DELETE FROM dbo.AssetInsurancePolicy WHERE AssetId = @AssetId;
        END
        
        -- Update or insert detail record based on new asset type
        IF @NewAssetType = 'Bank Account'
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.AssetBankAccount WHERE AssetId = @AssetId)
            BEGIN
                UPDATE dbo.AssetBankAccount
                SET AccountStatus = ISNULL(@AccountStatus, AccountStatus),
                    AccountOpeningDate = ISNULL(@AccountOpeningDate, AccountOpeningDate),
                    LastTransactionDate = ISNULL(@LastTransactionDate, LastTransactionDate),
                    InterestRate = ISNULL(@InterestRate, InterestRate),
                    AccountHolderName = ISNULL(@AccountHolderName, AccountHolderName),
                    BranchLocation = ISNULL(@BranchLocation, BranchLocation),
                    Currency = ISNULL(@Currency, Currency)
                WHERE AssetId = @AssetId;
            END
            ELSE
            BEGIN
                INSERT INTO dbo.AssetBankAccount (
                    AssetId, AccountStatus, AccountOpeningDate, LastTransactionDate,
                    InterestRate, AccountHolderName, BranchLocation, Currency
                )
                VALUES (
                    @AssetId, @AccountStatus, @AccountOpeningDate, @LastTransactionDate,
                    @InterestRate, @AccountHolderName, @BranchLocation, ISNULL(@Currency, 'USD')
                );
            END
        END
        ELSE IF @NewAssetType = 'Vehicle'
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.AssetVehicle WHERE AssetId = @AssetId)
            BEGIN
                UPDATE dbo.AssetVehicle
                SET VehicleMake = ISNULL(@VehicleMake, VehicleMake),
                    VehicleModel = ISNULL(@VehicleModel, VehicleModel),
                    VehicleYear = ISNULL(@VehicleYear, VehicleYear),
                    VehicleVIN = ISNULL(@VehicleVIN, VehicleVIN),
                    VehicleRegistration = ISNULL(@VehicleRegistration, VehicleRegistration),
                    VehicleCondition = ISNULL(@VehicleCondition, VehicleCondition),
                    VehicleMileage = ISNULL(@VehicleMileage, VehicleMileage)
                WHERE AssetId = @AssetId;
            END
            ELSE
            BEGIN
                INSERT INTO dbo.AssetVehicle (
                    AssetId, VehicleMake, VehicleModel, VehicleYear, VehicleVIN,
                    VehicleRegistration, VehicleCondition, VehicleMileage
                )
                VALUES (
                    @AssetId, @VehicleMake, @VehicleModel, @VehicleYear, @VehicleVIN,
                    @VehicleRegistration, @VehicleCondition, @VehicleMileage
                );
            END
        END
        ELSE IF @NewAssetType = 'Real Estate'
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.AssetRealEstate WHERE AssetId = @AssetId)
            BEGIN
                UPDATE dbo.AssetRealEstate
                SET PropertyAddress = ISNULL(@PropertyAddress, PropertyAddress),
                    PropertyType = ISNULL(@PropertyType, PropertyType),
                    PropertySize = ISNULL(@PropertySize, PropertySize),
                    PropertyCondition = ISNULL(@PropertyCondition, PropertyCondition),
                    PropertyTaxId = ISNULL(@PropertyTaxId, PropertyTaxId)
                WHERE AssetId = @AssetId;
            END
            ELSE
            BEGIN
                INSERT INTO dbo.AssetRealEstate (
                    AssetId, PropertyAddress, PropertyType, PropertySize,
                    PropertyCondition, PropertyTaxId
                )
                VALUES (
                    @AssetId, @PropertyAddress, @PropertyType, @PropertySize,
                    @PropertyCondition, @PropertyTaxId
                );
            END
        END
        ELSE IF @NewAssetType = 'Investment'
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.AssetInvestment WHERE AssetId = @AssetId)
            BEGIN
                UPDATE dbo.AssetInvestment
                SET AccountStatus = ISNULL(@AccountStatus, AccountStatus),
                    AccountOpeningDate = ISNULL(@AccountOpeningDate, AccountOpeningDate),
                    MaturityDate = ISNULL(@MaturityDate, MaturityDate),
                    InterestRate = ISNULL(@InterestRate, InterestRate),
                    Currency = ISNULL(@Currency, Currency),
                    InvestmentType = ISNULL(@InvestmentType, InvestmentType)
                WHERE AssetId = @AssetId;
            END
            ELSE
            BEGIN
                INSERT INTO dbo.AssetInvestment (
                    AssetId, AccountStatus, AccountOpeningDate, MaturityDate,
                    InterestRate, Currency, InvestmentType
                )
                VALUES (
                    @AssetId, @AccountStatus, @AccountOpeningDate, @MaturityDate,
                    @InterestRate, ISNULL(@Currency, 'USD'), @InvestmentType
                );
            END
        END
        ELSE IF @NewAssetType = 'Insurance Policy'
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.AssetInsurancePolicy WHERE AssetId = @AssetId)
            BEGIN
                UPDATE dbo.AssetInsurancePolicy
                SET PolicyNumber = ISNULL(@PolicyNumber, PolicyNumber),
                    PolicyType = ISNULL(@PolicyType, PolicyType),
                    PolicyStartDate = ISNULL(@PolicyStartDate, PolicyStartDate),
                    PolicyEndDate = ISNULL(@PolicyEndDate, PolicyEndDate),
                    PremiumAmount = ISNULL(@PremiumAmount, PremiumAmount)
                WHERE AssetId = @AssetId;
            END
            ELSE
            BEGIN
                INSERT INTO dbo.AssetInsurancePolicy (
                    AssetId, PolicyNumber, PolicyType, PolicyStartDate,
                    PolicyEndDate, PremiumAmount
                )
                VALUES (
                    @AssetId, @PolicyNumber, @PolicyType, @PolicyStartDate,
                    @PolicyEndDate, @PremiumAmount
                );
            END
        END
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Asset', CAST(@AssetId AS NVARCHAR(100)),
                    'Updated asset record');
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete Asset Record
CREATE PROCEDURE dbo.SP_DeleteAssetRecord
    @AssetId INT,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Assets WHERE AssetId = @AssetId)
        BEGIN
            SET @ErrorMessage = 'Asset record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check for associated claims
        DECLARE @ClaimCount INT;
        SELECT @ClaimCount = COUNT(*) FROM dbo.Claims WHERE AssetId = @AssetId;
        
        IF @ClaimCount > 0
        BEGIN
            SET @ErrorMessage = 'Cannot delete asset with ' + CAST(@ClaimCount AS NVARCHAR(10)) + ' associated claims';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get asset type for audit
        DECLARE @AssetType NVARCHAR(100);
        SELECT @AssetType = AssetType FROM dbo.Assets WHERE AssetId = @AssetId;
        
        -- Delete record
        DELETE FROM dbo.Assets WHERE AssetId = @AssetId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'DELETE', 'Asset', CAST(@AssetId AS NVARCHAR(100)),
                    'Deleted asset: ' + @AssetType);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Get Assets by Deceased (Updated to join with detail tables)
CREATE PROCEDURE dbo.SP_GetAssetsByDeceased
    @DeceasedId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @DeceasedId IS NULL
    BEGIN
        -- Return all assets with details from appropriate detail tables
        SELECT 
            a.AssetId,
            a.DeceasedId,
            a.InstitutionId,
            a.AssetType,
            a.Identifier,
            a.EstimatedValue,
            a.BeneficiaryInfo,
            a.Documentation,
            a.Notes,
            a.CreatedAt,
            d.FirstName + ' ' + d.LastName AS DeceasedName,
            i.Name AS InstitutionName,
            i.Type AS InstitutionType,
            -- Bank Account fields
            ba.AccountStatus,
            ba.AccountOpeningDate,
            ba.LastTransactionDate,
            ba.InterestRate,
            ba.AccountHolderName,
            ba.BranchLocation,
            ba.Currency,
            -- Vehicle fields
            v.VehicleMake,
            v.VehicleModel,
            v.VehicleYear,
            v.VehicleVIN,
            v.VehicleRegistration,
            v.VehicleCondition,
            v.VehicleMileage,
            -- Real Estate fields
            re.PropertyAddress,
            re.PropertyType,
            re.PropertySize,
            re.PropertyCondition,
            re.PropertyTaxId,
            -- Investment fields
            inv.AccountStatus AS InvestmentAccountStatus,
            inv.AccountOpeningDate AS InvestmentAccountOpeningDate,
            inv.MaturityDate,
            inv.InterestRate AS InvestmentInterestRate,
            inv.Currency AS InvestmentCurrency,
            inv.InvestmentType,
            -- Insurance Policy fields
            ip.PolicyNumber,
            ip.PolicyType,
            ip.PolicyStartDate,
            ip.PolicyEndDate,
            ip.PremiumAmount
        FROM dbo.Assets a
        INNER JOIN dbo.Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId
        LEFT JOIN dbo.AssetBankAccount ba ON a.AssetId = ba.AssetId
        LEFT JOIN dbo.AssetVehicle v ON a.AssetId = v.AssetId
        LEFT JOIN dbo.AssetRealEstate re ON a.AssetId = re.AssetId
        LEFT JOIN dbo.AssetInvestment inv ON a.AssetId = inv.AssetId
        LEFT JOIN dbo.AssetInsurancePolicy ip ON a.AssetId = ip.AssetId
        ORDER BY d.LastName, d.FirstName, a.AssetType;
    END
    ELSE
    BEGIN
        -- Return assets for specific deceased
        SELECT 
            a.AssetId,
            a.DeceasedId,
            a.InstitutionId,
            a.AssetType,
            a.Identifier,
            a.EstimatedValue,
            a.BeneficiaryInfo,
            a.Documentation,
            a.Notes,
            a.CreatedAt,
            d.FirstName + ' ' + d.LastName AS DeceasedName,
            i.Name AS InstitutionName,
            i.Type AS InstitutionType,
            -- Bank Account fields
            ba.AccountStatus,
            ba.AccountOpeningDate,
            ba.LastTransactionDate,
            ba.InterestRate,
            ba.AccountHolderName,
            ba.BranchLocation,
            ba.Currency,
            -- Vehicle fields
            v.VehicleMake,
            v.VehicleModel,
            v.VehicleYear,
            v.VehicleVIN,
            v.VehicleRegistration,
            v.VehicleCondition,
            v.VehicleMileage,
            -- Real Estate fields
            re.PropertyAddress,
            re.PropertyType,
            re.PropertySize,
            re.PropertyCondition,
            re.PropertyTaxId,
            -- Investment fields
            inv.AccountStatus AS InvestmentAccountStatus,
            inv.AccountOpeningDate AS InvestmentAccountOpeningDate,
            inv.MaturityDate,
            inv.InterestRate AS InvestmentInterestRate,
            inv.Currency AS InvestmentCurrency,
            inv.InvestmentType,
            -- Insurance Policy fields
            ip.PolicyNumber,
            ip.PolicyType,
            ip.PolicyStartDate,
            ip.PolicyEndDate,
            ip.PremiumAmount
        FROM dbo.Assets a
        INNER JOIN dbo.Deceased d ON a.DeceasedId = d.DeceasedId
        INNER JOIN dbo.Institutions i ON a.InstitutionId = i.InstitutionId
        LEFT JOIN dbo.AssetBankAccount ba ON a.AssetId = ba.AssetId
        LEFT JOIN dbo.AssetVehicle v ON a.AssetId = v.AssetId
        LEFT JOIN dbo.AssetRealEstate re ON a.AssetId = re.AssetId
        LEFT JOIN dbo.AssetInvestment inv ON a.AssetId = inv.AssetId
        LEFT JOIN dbo.AssetInsurancePolicy ip ON a.AssetId = ip.AssetId
        WHERE a.DeceasedId = @DeceasedId
        ORDER BY a.AssetType;
    END
END;
GO

-- ============================================================================
-- CLAIMANTS OPERATIONS
-- ============================================================================

-- Stored Procedure: Create Claimant with Validation
CREATE PROCEDURE dbo.SP_CreateClaimantWithValidation
    @NationalId NVARCHAR(50) = NULL,
    @FirstName NVARCHAR(100),
    @MiddleName NVARCHAR(100) = NULL,
    @LastName NVARCHAR(100),
    @DateOfBirth DATE = NULL,
    @Gender NVARCHAR(20) = NULL,
    @Relationship NVARCHAR(100) = NULL,
    @Contact NVARCHAR(200) = NULL,
    @Email NVARCHAR(200) = NULL,
    @Phone NVARCHAR(50) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Occupation NVARCHAR(100) = NULL,
    @MaritalStatus NVARCHAR(50) = NULL,
    @AlternateContact NVARCHAR(200) = NULL,
    @RelationshipProof NVARCHAR(500) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @ClaimantId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @ClaimantId = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validation: FirstName is required
        IF @FirstName IS NULL OR LEN(LTRIM(RTRIM(@FirstName))) = 0
        BEGIN
            SET @ErrorMessage = 'FirstName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: LastName is required
        IF @LastName IS NULL OR LEN(LTRIM(RTRIM(@LastName))) = 0
        BEGIN
            SET @ErrorMessage = 'LastName is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Check for duplicate NationalId if provided
        IF @NationalId IS NOT NULL AND EXISTS (SELECT 1 FROM dbo.Claimants WHERE NationalId = @NationalId)
        BEGIN
            SET @ErrorMessage = 'NationalId already exists';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Insert record
        INSERT INTO dbo.Claimants (
            NationalId, FirstName, MiddleName, LastName, DateOfBirth, Gender,
            Relationship, Contact, Email, Phone, Address, Occupation, MaritalStatus,
            AlternateContact, RelationshipProof, Notes
        )
        VALUES (
            @NationalId, @FirstName, @MiddleName, @LastName, @DateOfBirth, @Gender,
            @Relationship, @Contact, @Email, @Phone, @Address, @Occupation, @MaritalStatus,
            @AlternateContact, @RelationshipProof, @Notes
        );
        
        SET @ClaimantId = SCOPE_IDENTITY();
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Claimant', CAST(@ClaimantId AS NVARCHAR(100)),
                    'Created claimant: ' + @FirstName + ' ' + @LastName);
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update Claimant Record
CREATE PROCEDURE dbo.SP_UpdateClaimantRecord
    @ClaimantId INT,
    @NationalId NVARCHAR(50) = NULL,
    @FirstName NVARCHAR(100) = NULL,
    @MiddleName NVARCHAR(100) = NULL,
    @LastName NVARCHAR(100) = NULL,
    @DateOfBirth DATE = NULL,
    @Gender NVARCHAR(20) = NULL,
    @Relationship NVARCHAR(100) = NULL,
    @Contact NVARCHAR(200) = NULL,
    @Email NVARCHAR(200) = NULL,
    @Phone NVARCHAR(50) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Occupation NVARCHAR(100) = NULL,
    @MaritalStatus NVARCHAR(50) = NULL,
    @AlternateContact NVARCHAR(200) = NULL,
    @RelationshipProof NVARCHAR(500) = NULL,
    @Notes NVARCHAR(1000) = NULL,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Claimants WHERE ClaimantId = @ClaimantId)
        BEGIN
            SET @ErrorMessage = 'Claimant record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: If FirstName is provided, it cannot be empty
        IF @FirstName IS NOT NULL AND LEN(LTRIM(RTRIM(@FirstName))) = 0
        BEGIN
            SET @ErrorMessage = 'FirstName cannot be empty';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: If LastName is provided, it cannot be empty
        IF @LastName IS NOT NULL AND LEN(LTRIM(RTRIM(@LastName))) = 0
        BEGIN
            SET @ErrorMessage = 'LastName cannot be empty';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Check for duplicate NationalId if provided and changed
        IF @NationalId IS NOT NULL 
           AND EXISTS (SELECT 1 FROM dbo.Claimants WHERE NationalId = @NationalId AND ClaimantId != @ClaimantId)
        BEGIN
            SET @ErrorMessage = 'NationalId already exists for another record';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update record (only update provided fields)
        UPDATE dbo.Claimants
        SET NationalId = ISNULL(@NationalId, NationalId),
            FirstName = ISNULL(@FirstName, FirstName),
            MiddleName = ISNULL(@MiddleName, MiddleName),
            LastName = ISNULL(@LastName, LastName),
            DateOfBirth = ISNULL(@DateOfBirth, DateOfBirth),
            Gender = ISNULL(@Gender, Gender),
            Relationship = ISNULL(@Relationship, Relationship),
            Contact = ISNULL(@Contact, Contact),
            Email = ISNULL(@Email, Email),
            Phone = ISNULL(@Phone, Phone),
            Address = ISNULL(@Address, Address),
            Occupation = ISNULL(@Occupation, Occupation),
            MaritalStatus = ISNULL(@MaritalStatus, MaritalStatus),
            AlternateContact = ISNULL(@AlternateContact, AlternateContact),
            RelationshipProof = ISNULL(@RelationshipProof, RelationshipProof),
            Notes = ISNULL(@Notes, Notes)
        WHERE ClaimantId = @ClaimantId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Claimant', CAST(@ClaimantId AS NVARCHAR(100)),
                    'Updated claimant record');
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete Claimant Record
CREATE PROCEDURE dbo.SP_DeleteClaimantRecord
    @ClaimantId INT,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Claimants WHERE ClaimantId = @ClaimantId)
        BEGIN
            SET @ErrorMessage = 'Claimant record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check for associated claims
        DECLARE @ClaimCount INT;
        SELECT @ClaimCount = COUNT(*) FROM dbo.Claims WHERE ClaimantId = @ClaimantId;
        
        IF @ClaimCount > 0
        BEGIN
            SET @ErrorMessage = 'Cannot delete claimant with ' + CAST(@ClaimCount AS NVARCHAR(10)) + ' associated claims';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get name for audit
        DECLARE @FirstName NVARCHAR(100);
        DECLARE @LastName NVARCHAR(100);
        SELECT @FirstName = FirstName, @LastName = LastName
        FROM dbo.Claimants WHERE ClaimantId = @ClaimantId;
        
        -- Delete record
        DELETE FROM dbo.Claimants WHERE ClaimantId = @ClaimantId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'DELETE', 'Claimant', CAST(@ClaimantId AS NVARCHAR(100)),
                    'Deleted claimant: ' + @FirstName + ' ' + @LastName);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- ============================================================================
-- INSTITUTIONS OPERATIONS
-- ============================================================================

-- Stored Procedure: Create Institution
CREATE PROCEDURE dbo.SP_CreateInstitution
    @Name NVARCHAR(200),
    @Type NVARCHAR(100) = NULL,
    @Contact NVARCHAR(200) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Phone NVARCHAR(50) = NULL,
    @UserId INT = NULL,
    @InstitutionId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @InstitutionId = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validation: Name is required
        IF @Name IS NULL OR LEN(LTRIM(RTRIM(@Name))) = 0
        BEGIN
            SET @ErrorMessage = 'Name is required';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Check for duplicate name
        IF EXISTS (SELECT 1 FROM dbo.Institutions WHERE Name = @Name)
        BEGIN
            SET @ErrorMessage = 'Institution name already exists';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Insert record
        INSERT INTO dbo.Institutions (Name, Type, Contact, Address, Phone)
        VALUES (@Name, @Type, @Contact, @Address, @Phone);
        
        SET @InstitutionId = SCOPE_IDENTITY();
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'CREATE', 'Institution', CAST(@InstitutionId AS NVARCHAR(100)),
                    'Created institution: ' + @Name);
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update Institution
CREATE PROCEDURE dbo.SP_UpdateInstitution
    @InstitutionId INT,
    @Name NVARCHAR(200) = NULL,
    @Type NVARCHAR(100) = NULL,
    @Contact NVARCHAR(200) = NULL,
    @Address NVARCHAR(500) = NULL,
    @Phone NVARCHAR(50) = NULL,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Institutions WHERE InstitutionId = @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: If Name is provided, it cannot be empty
        IF @Name IS NOT NULL AND LEN(LTRIM(RTRIM(@Name))) = 0
        BEGIN
            SET @ErrorMessage = 'Name cannot be empty';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validation: Check for duplicate name if provided and changed
        IF @Name IS NOT NULL 
           AND EXISTS (SELECT 1 FROM dbo.Institutions WHERE Name = @Name AND InstitutionId != @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution name already exists for another record';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update record (only update provided fields)
        UPDATE dbo.Institutions
        SET Name = ISNULL(@Name, Name),
            Type = ISNULL(@Type, Type),
            Contact = ISNULL(@Contact, Contact),
            Address = ISNULL(@Address, Address),
            Phone = ISNULL(@Phone, Phone)
        WHERE InstitutionId = @InstitutionId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Institution', CAST(@InstitutionId AS NVARCHAR(100)),
                    'Updated institution record');
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete Institution
CREATE PROCEDURE dbo.SP_DeleteInstitution
    @InstitutionId INT,
    @UserId INT = NULL,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate record exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Institutions WHERE InstitutionId = @InstitutionId)
        BEGIN
            SET @ErrorMessage = 'Institution record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check for associated assets
        DECLARE @AssetCount INT;
        SELECT @AssetCount = COUNT(*) FROM dbo.Assets WHERE InstitutionId = @InstitutionId;
        
        IF @AssetCount > 0
        BEGIN
            SET @ErrorMessage = 'Cannot delete institution with ' + CAST(@AssetCount AS NVARCHAR(10)) + ' associated assets';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get name for audit
        DECLARE @Name NVARCHAR(200);
        SELECT @Name = Name FROM dbo.Institutions WHERE InstitutionId = @InstitutionId;
        
        -- Delete record
        DELETE FROM dbo.Institutions WHERE InstitutionId = @InstitutionId;
        
        -- Audit logging
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'DELETE', 'Institution', CAST(@InstitutionId AS NVARCHAR(100)),
                    'Deleted institution: ' + @Name);
        END
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- ============================================================================
-- Stored Procedure: SP_CreateUserByAdmin (Updated with SQL Server Login Support)
-- Purpose: Create a new user account - only allowed by Admin users
-- Security: Enforces admin-only user creation at database level
-- Enhancement: Automatically creates SQL Server login with appropriate permissions
-- ============================================================================
CREATE PROCEDURE dbo.SP_CreateUserByAdmin
    @Username NVARCHAR(100),
    @PasswordHash VARBINARY(256),
    @Role NVARCHAR(50),
    @CreatedByUserId INT,  -- ID of admin user creating this account
    @Email NVARCHAR(200) = NULL,
    @CreateSQLLogin BIT = 1, -- Whether to create SQL Server login (default: yes)
    @SQLLoginPassword NVARCHAR(255) = NULL, -- Password for SQL Server login (if different from app password)
    @NewUserId INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @NewUserId = NULL;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check 1: Verify the creator is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @CreatedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can create new users.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Security Check 2: Verify username doesn't already exist
        IF EXISTS (SELECT 1 FROM dbo.Users WHERE Username = @Username)
        BEGIN
            SET @ErrorMessage = 'Username already exists.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Security Check 3: Validate role
        IF @Role NOT IN ('Admin', 'Staff', 'Viewer')
        BEGIN
            SET @ErrorMessage = 'Invalid role. Must be Admin, Staff, or Viewer.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Security Check 4: Validate password hash is not null
        IF @PasswordHash IS NULL OR DATALENGTH(@PasswordHash) = 0
        BEGIN
            SET @ErrorMessage = 'Password hash is required.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Create the user in application table
        INSERT INTO dbo.Users (Username, PasswordHash, Role, Email, CreatedAt, IsActive)
        VALUES (@Username, @PasswordHash, @Role, @Email, SYSUTCDATETIME(), 1);
        
        SET @NewUserId = SCOPE_IDENTITY();
        
        -- Create SQL Server login if requested
        IF @CreateSQLLogin = 1
        BEGIN
            DECLARE @SQLLoginPasswordFinal NVARCHAR(255);
            SET @SQLLoginPasswordFinal = ISNULL(@SQLLoginPassword, 'TempPassword123!'); -- Default password if not provided
            
            DECLARE @LoginSuccess BIT;
            DECLARE @LoginError NVARCHAR(500);
            
            EXEC dbo.SP_CreateSQLServerLogin
                @Username = @Username,
                @Password = @SQLLoginPasswordFinal,
                @Role = @Role,
                @CreatedByUserId = @CreatedByUserId,
                @Success = @LoginSuccess OUTPUT,
                @ErrorMessage = @LoginError OUTPUT;
            
            IF @LoginSuccess = 0
            BEGIN
                -- If SQL login creation fails, rollback user creation
                SET @ErrorMessage = 'User created but SQL Server login creation failed: ' + @LoginError;
                ROLLBACK TRANSACTION;
                RETURN;
            END
        END
        
        -- Audit log entry
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@CreatedByUserId, 'CREATE', 'User', CAST(@NewUserId AS NVARCHAR(100)),
                'User account created: ' + @Username + ' with role ' + @Role + 
                CASE WHEN @CreateSQLLogin = 1 THEN ' (SQL Server login created)' ELSE '' END);
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- ============================================================================
-- SQL SERVER LOGIN MANAGEMENT (Database-Level Authentication)
-- ============================================================================

-- Stored Procedure: Create SQL Server Login and Grant Permissions
-- Purpose: Creates a SQL Server login and grants appropriate permissions based on role
-- Security: Only admins can execute this
CREATE PROCEDURE dbo.SP_CreateSQLServerLogin
    @Username NVARCHAR(100),
    @Password NVARCHAR(255), -- Plain text password (will be hashed by SQL Server)
    @Role NVARCHAR(50), -- Admin, Staff, or Viewer
    @CreatedByUserId INT, -- Admin user creating this login
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check: Verify the creator is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @CreatedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can create SQL Server logins.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validate role
        IF @Role NOT IN ('Admin', 'Staff', 'Viewer')
        BEGIN
            SET @ErrorMessage = 'Invalid role. Must be Admin, Staff, or Viewer.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check if login already exists
        IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @Username)
        BEGIN
            SET @ErrorMessage = 'SQL Server login already exists.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Create SQL Server login
        DECLARE @SQL NVARCHAR(MAX);
        SET @SQL = 'CREATE LOGIN [' + @Username + '] WITH PASSWORD = ''' + @Password + ''', DEFAULT_DATABASE = [FARVS]';
        EXEC sp_executesql @SQL;
        
        -- Create database user
        SET @SQL = 'CREATE USER [' + @Username + '] FOR LOGIN [' + @Username + ']';
        EXEC sp_executesql @SQL;
        
        -- Grant permissions based on role
        IF @Role = 'Admin'
        BEGIN
            -- Admin: Full access
            SET @SQL = 'ALTER ROLE db_owner ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @Role = 'Staff'
        BEGIN
            -- Staff: Read/Write access to all tables, can execute stored procedures
            SET @SQL = 'ALTER ROLE db_datareader ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'ALTER ROLE db_datawriter ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'GRANT EXECUTE ON SCHEMA::dbo TO [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @Role = 'Viewer'
        BEGIN
            -- Viewer: Read-only access
            SET @SQL = 'ALTER ROLE db_datareader ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        
        -- Audit logging
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@CreatedByUserId, 'CREATE', 'SQLServerLogin', @Username,
                'Created SQL Server login: ' + @Username + ' with role ' + @Role);
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Update SQL Server Login Permissions
-- Purpose: Updates permissions when user role changes
CREATE PROCEDURE dbo.SP_UpdateSQLServerLoginPermissions
    @Username NVARCHAR(100),
    @OldRole NVARCHAR(50),
    @NewRole NVARCHAR(50),
    @UpdatedByUserId INT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check: Verify the updater is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @UpdatedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can update SQL Server login permissions.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check if login exists
        IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @Username)
        BEGIN
            SET @ErrorMessage = 'SQL Server login not found.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        DECLARE @SQL NVARCHAR(MAX);
        
        -- Remove old role permissions
        IF @OldRole = 'Admin'
        BEGIN
            SET @SQL = 'ALTER ROLE db_owner DROP MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @OldRole = 'Staff'
        BEGIN
            SET @SQL = 'ALTER ROLE db_datareader DROP MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'ALTER ROLE db_datawriter DROP MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'REVOKE EXECUTE ON SCHEMA::dbo FROM [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @OldRole = 'Viewer'
        BEGIN
            SET @SQL = 'ALTER ROLE db_datareader DROP MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        
        -- Grant new role permissions
        IF @NewRole = 'Admin'
        BEGIN
            SET @SQL = 'ALTER ROLE db_owner ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @NewRole = 'Staff'
        BEGIN
            SET @SQL = 'ALTER ROLE db_datareader ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'ALTER ROLE db_datawriter ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
            SET @SQL = 'GRANT EXECUTE ON SCHEMA::dbo TO [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        ELSE IF @NewRole = 'Viewer'
        BEGIN
            SET @SQL = 'ALTER ROLE db_datareader ADD MEMBER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        
        -- Audit logging
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@UpdatedByUserId, 'UPDATE', 'SQLServerLogin', @Username,
                'Updated SQL Server login permissions: ' + @Username + ' from ' + @OldRole + ' to ' + @NewRole);
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Drop SQL Server Login
-- Purpose: Removes SQL Server login when user is deleted
CREATE PROCEDURE dbo.SP_DropSQLServerLogin
    @Username NVARCHAR(100),
    @DeletedByUserId INT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check: Verify the deleter is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @DeletedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can drop SQL Server logins.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Check if login exists
        IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @Username)
        BEGIN
            SET @ErrorMessage = 'SQL Server login not found.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Drop database user first
        IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = @Username)
        BEGIN
            DECLARE @SQL NVARCHAR(MAX);
            SET @SQL = 'DROP USER [' + @Username + ']';
            EXEC sp_executesql @SQL;
        END
        
        -- Drop login
        SET @SQL = 'DROP LOGIN [' + @Username + ']';
        EXEC sp_executesql @SQL;
        
        -- Audit logging
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@DeletedByUserId, 'DELETE', 'SQLServerLogin', @Username,
                'Dropped SQL Server login: ' + @Username);
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Update SP_CreateUserByAdmin to also create SQL Server login
-- Note: This requires modifying the existing procedure
-- We'll add a parameter to optionally create SQL Server login

-- ============================================================================
-- USER MANAGEMENT OPERATIONS (Update and Delete with SQL Server Login Support)
-- ============================================================================

-- Stored Procedure: Update User (with SQL Server login permission updates)
-- Purpose: Update user information and update SQL Server login permissions if role changes
CREATE PROCEDURE dbo.SP_UpdateUserByAdmin
    @UserId INT,
    @Username NVARCHAR(100) = NULL,
    @PasswordHash VARBINARY(256) = NULL,
    @Role NVARCHAR(50) = NULL,
    @Email NVARCHAR(200) = NULL,
    @UpdatedByUserId INT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check: Verify the updater is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @UpdatedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can update users.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validate user exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE UserId = @UserId)
        BEGIN
            SET @ErrorMessage = 'User not found.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get current user data
        DECLARE @CurrentUsername NVARCHAR(100);
        DECLARE @CurrentRole NVARCHAR(50);
        SELECT @CurrentUsername = Username, @CurrentRole = Role
        FROM dbo.Users WHERE UserId = @UserId;
        
        -- Validate username uniqueness if changing
        IF @Username IS NOT NULL AND @Username != @CurrentUsername
        BEGIN
            IF EXISTS (SELECT 1 FROM dbo.Users WHERE Username = @Username AND UserId != @UserId)
            BEGIN
                SET @ErrorMessage = 'Username already exists.';
                ROLLBACK TRANSACTION;
                RETURN;
            END
        END
        
        -- Validate role if provided
        IF @Role IS NOT NULL AND @Role NOT IN ('Admin', 'Staff', 'Viewer')
        BEGIN
            SET @ErrorMessage = 'Invalid role. Must be Admin, Staff, or Viewer.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update user record
        UPDATE dbo.Users
        SET Username = ISNULL(@Username, Username),
            PasswordHash = ISNULL(@PasswordHash, PasswordHash),
            Role = ISNULL(@Role, Role),
            Email = ISNULL(@Email, Email)
        WHERE UserId = @UserId;
        
        -- Update SQL Server login permissions if role changed
        DECLARE @NewRole NVARCHAR(50) = ISNULL(@Role, @CurrentRole);
        IF @NewRole != @CurrentRole
        BEGIN
            DECLARE @LoginSuccess BIT;
            DECLARE @LoginError NVARCHAR(500);
            
            EXEC dbo.SP_UpdateSQLServerLoginPermissions
                @Username = @CurrentUsername,
                @OldRole = @CurrentRole,
                @NewRole = @NewRole,
                @UpdatedByUserId = @UpdatedByUserId,
                @Success = @LoginSuccess OUTPUT,
                @ErrorMessage = @LoginError OUTPUT;
            
            IF @LoginSuccess = 0
            BEGIN
                SET @ErrorMessage = 'User updated but SQL Server login permission update failed: ' + @LoginError;
                ROLLBACK TRANSACTION;
                RETURN;
            END
        END
        
        -- Audit logging
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@UpdatedByUserId, 'UPDATE', 'User', CAST(@UserId AS NVARCHAR(100)),
                'Updated user: ' + ISNULL(@Username, @CurrentUsername) + 
                CASE WHEN @NewRole != @CurrentRole THEN ' (role changed from ' + @CurrentRole + ' to ' + @NewRole + ')' ELSE '' END);
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Delete User (with SQL Server login deletion)
-- Purpose: Delete user account and associated SQL Server login
CREATE PROCEDURE dbo.SP_DeleteUserByAdmin
    @UserId INT,
    @DeletedByUserId INT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Security Check: Verify the deleter is an Admin
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Users 
            WHERE UserId = @DeletedByUserId AND Role = 'Admin' AND IsActive = 1
        )
        BEGIN
            SET @ErrorMessage = 'Access Denied: Only administrators can delete users.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Prevent deleting yourself
        IF @UserId = @DeletedByUserId
        BEGIN
            SET @ErrorMessage = 'You cannot delete your own account.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Validate user exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE UserId = @UserId)
        BEGIN
            SET @ErrorMessage = 'User not found.';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get username for SQL Server login deletion
        DECLARE @Username NVARCHAR(100);
        SELECT @Username = Username FROM dbo.Users WHERE UserId = @UserId;
        
        -- Drop SQL Server login if it exists
        IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = @Username)
        BEGIN
            DECLARE @LoginSuccess BIT;
            DECLARE @LoginError NVARCHAR(500);
            
            EXEC dbo.SP_DropSQLServerLogin
                @Username = @Username,
                @DeletedByUserId = @DeletedByUserId,
                @Success = @LoginSuccess OUTPUT,
                @ErrorMessage = @LoginError OUTPUT;
            
            -- Log warning but continue with user deletion
            IF @LoginSuccess = 0
            BEGIN
                -- Log warning but don't fail the transaction
                INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
                VALUES (@DeletedByUserId, 'WARNING', 'User', CAST(@UserId AS NVARCHAR(100)),
                        'User deleted but SQL Server login deletion failed: ' + @LoginError);
            END
        END
        
        -- Delete user record
        DELETE FROM dbo.Users WHERE UserId = @UserId;
        
        -- Audit logging
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@DeletedByUserId, 'DELETE', 'User', CAST(@UserId AS NVARCHAR(100)),
                'Deleted user: ' + @Username);
        
        SET @Success = 1;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Get All Users
-- Purpose: Retrieve all users for display
CREATE PROCEDURE dbo.SP_GetAllUsers
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        UserId,
        Username,
        Role,
        Email,
        CreatedAt,
        IsActive
    FROM dbo.Users
    ORDER BY Username;
END;
GO

-- ============================================================================
-- SECTION 7: TRIGGERS (Automatic actions on data changes)
-- ============================================================================

-- Trigger: Auto-update timestamps when claim status changes
CREATE TRIGGER dbo.TR_Claims_StatusChange
ON dbo.Claims
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update VerifiedAt when status changes to Verified
    UPDATE c
    SET VerifiedAt = CASE 
        WHEN i.Status = 'Verified' AND c.VerifiedAt IS NULL THEN GETDATE()
        ELSE c.VerifiedAt
    END,
    SettledAt = CASE
        WHEN i.Status = 'Settled' AND c.SettledAt IS NULL THEN GETDATE()
        ELSE c.SettledAt
    END
    FROM dbo.Claims c
    INNER JOIN inserted i ON c.ClaimId = i.ClaimId
    INNER JOIN deleted d ON c.ClaimId = d.ClaimId
    WHERE i.Status != d.Status;
END;
GO

-- Trigger: Prevent invalid status transitions (validates before update completes)
CREATE TRIGGER dbo.TR_Claims_PreventInvalidStatus
ON dbo.Claims
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check for invalid transitions and rollback if found
    IF EXISTS (
        SELECT 1 
        FROM inserted i
        INNER JOIN deleted d ON i.ClaimId = d.ClaimId
        WHERE 
            -- Cannot go backwards: Settled -> Verified or Settled -> Pending
            (d.Status = 'Settled' AND i.Status IN ('Verified', 'Pending'))
            OR
            -- Cannot skip status: Pending -> Settled (must go through Verified)
            (d.Status = 'Pending' AND i.Status = 'Settled')
            OR
            -- Cannot go from Verified back to Pending
            (d.Status = 'Verified' AND i.Status = 'Pending')
    )
    BEGIN
        -- Rollback the transaction
        ROLLBACK TRANSACTION;
        RAISERROR('Invalid status transition. Valid transitions: Pending->Verified->Settled', 16, 1);
        RETURN;
    END
END;
GO

-- Trigger: Auto-close case when all claims are settled
CREATE TRIGGER dbo.TR_Claims_AutoCloseCase
ON dbo.Claims
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- When a claim is settled, check if all claims in the case are settled
    UPDATE Cases
    SET Status = 'Closed',
        ClosedAt = GETDATE()
    FROM dbo.Cases
    WHERE Cases.ClaimId IN (SELECT ClaimId FROM inserted WHERE Status = 'Settled')
        AND Cases.Status != 'Closed'
        AND NOT EXISTS (
            -- Check if there are any non-settled claims in this case
            SELECT 1 
            FROM dbo.Claims c
            WHERE c.ClaimId = Cases.ClaimId
                AND c.Status != 'Settled'
        );
END;
GO

-- Trigger: Log asset creation in audit log
CREATE TRIGGER dbo.TR_Assets_AfterInsert
ON dbo.Assets
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Note: In production, get UserId from session context or application
    INSERT INTO dbo.AuditLog (Action, Entity, EntityId, Details)
    SELECT 
        'CREATE',
        'Asset',
        CAST(AssetId AS NVARCHAR(100)),
        'Asset created: ' + AssetType + ' for Deceased ' + CAST(DeceasedId AS NVARCHAR(10))
    FROM inserted;
END;
GO

-- Trigger: Log deceased updates
CREATE TRIGGER dbo.TR_Deceased_AfterUpdate
ON dbo.Deceased
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO dbo.AuditLog (Action, Entity, EntityId, Details)
    SELECT 
        'UPDATE',
        'Deceased',
        CAST(i.DeceasedId AS NVARCHAR(100)),
        'Deceased record updated: ' + i.FirstName + ' ' + i.LastName
    FROM inserted i
    INNER JOIN deleted d ON i.DeceasedId = d.DeceasedId
    WHERE i.FirstName != d.FirstName 
       OR i.LastName != d.LastName
       OR i.DateOfDeath != d.DateOfDeath;
END;
GO

-- ============================================================================

-- Query 2: Demonstrate transaction usage - Update claim status
/*
DECLARE @ClaimId INT = 1;
DECLARE @NewStatus NVARCHAR(50) = 'Verified';
DECLARE @UserId INT = 1;
DECLARE @Success BIT;
DECLARE @ErrorMessage NVARCHAR(500);

EXEC dbo.SP_UpdateClaimStatus 
    @ClaimId = @ClaimId,
    @NewStatus = @NewStatus,
    @UserId = @UserId,
    @Success = @Success OUTPUT,
    @ErrorMessage = @ErrorMessage OUTPUT;

SELECT @Success AS Success, @ErrorMessage AS ErrorMessage;
*/

-- Query 3: Use view for simplified reporting
/*
SELECT * FROM dbo.VW_System_Statistics;
*/

-- Query 4: Demonstrate stored procedure with transaction
/*
DECLARE @AssetId INT = 1;
DECLARE @ClaimantId INT = 1;
DECLARE @ClaimId INT;
DECLARE @ErrorMessage NVARCHAR(500);

EXEC dbo.SP_CreateClaimWithValidation
    @AssetId = @AssetId,
    @ClaimantId = @ClaimantId,
    @UserId = 1,
    @ClaimId = @ClaimId OUTPUT,
    @ErrorMessage = @ErrorMessage OUTPUT;

SELECT @ClaimId AS NewClaimId, @ErrorMessage AS ErrorMessage;
*/

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
PRINT 'FARVS Database Schema created successfully!';
PRINT 'All database components (tables, views, stored procedures, triggers, transactions) are ready.';
GO
