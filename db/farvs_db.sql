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

-- Drop stored procedures
IF OBJECT_ID('dbo.SP_CreateClaimWithValidation', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateClaimWithValidation;
IF OBJECT_ID('dbo.SP_UpdateClaimStatus', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_UpdateClaimStatus;
IF OBJECT_ID('dbo.SP_DeleteDeceasedWithAssets', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_DeleteDeceasedWithAssets;
IF OBJECT_ID('dbo.SP_GetPendingClaims', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_GetPendingClaims;
IF OBJECT_ID('dbo.SP_BatchCreateAssets', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_BatchCreateAssets;
IF OBJECT_ID('dbo.SP_CreateUserByAdmin', 'P') IS NOT NULL DROP PROCEDURE dbo.SP_CreateUserByAdmin;
GO

-- Drop tables (reverse dependency order)
IF OBJECT_ID('dbo.Attachments', 'U') IS NOT NULL DROP TABLE dbo.Attachments;
IF OBJECT_ID('dbo.Notes', 'U') IS NOT NULL DROP TABLE dbo.Notes;
IF OBJECT_ID('dbo.Tasks', 'U') IS NOT NULL DROP TABLE dbo.Tasks;
IF OBJECT_ID('dbo.Cases', 'U') IS NOT NULL DROP TABLE dbo.Cases;
IF OBJECT_ID('dbo.StatusHistory', 'U') IS NOT NULL DROP TABLE dbo.StatusHistory;
IF OBJECT_ID('dbo.AssetValuations', 'U') IS NOT NULL DROP TABLE dbo.AssetValuations;
IF OBJECT_ID('dbo.AssetTypes', 'U') IS NOT NULL DROP TABLE dbo.AssetTypes;
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
CREATE PROCEDURE dbo.SP_DeleteDeceasedWithAssets
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
        -- Validate deceased exists
        IF NOT EXISTS (SELECT 1 FROM dbo.Deceased WHERE DeceasedId = @DeceasedId)
        BEGIN
            SET @ErrorMessage = 'Deceased record not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Get asset count for audit
        DECLARE @AssetCount INT;
        SELECT @AssetCount = COUNT(*) FROM dbo.Assets WHERE DeceasedId = @DeceasedId;
        
        -- Delete will cascade to Assets and Claims due to foreign key constraints
        DELETE FROM dbo.Deceased WHERE DeceasedId = @DeceasedId;
        
        -- Log audit
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'DELETE', 'Deceased', CAST(@DeceasedId AS NVARCHAR(100)),
                    'Deleted deceased and ' + CAST(@AssetCount AS NVARCHAR(10)) + ' associated assets');
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

-- Stored Procedure: Get Pending Claims (with filtering)
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
CREATE PROCEDURE dbo.SP_BulkVerifyClaims
    @ClaimIds NVARCHAR(MAX), -- Comma-separated list: "1,2,3,4,5"
    @UserId INT = NULL,
    @VerifiedCount INT OUTPUT,
    @FailedCount INT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @VerifiedCount = 0;
    SET @FailedCount = 0;
    SET @ErrorMessage = NULL;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        DECLARE @ClaimId INT;
        DECLARE @Pos INT = 1;
        DECLARE @NextPos INT;
        DECLARE @Item NVARCHAR(50);
        
        -- Process each claim ID
        WHILE @Pos <= LEN(@ClaimIds)
        BEGIN
            BEGIN TRY
                -- Create savepoint before each claim update
                SAVE TRANSACTION Savepoint_BeforeClaim;
                
                SET @NextPos = CHARINDEX(',', @ClaimIds, @Pos);
                IF @NextPos = 0 SET @NextPos = LEN(@ClaimIds) + 1;
                
                SET @Item = LTRIM(RTRIM(SUBSTRING(@ClaimIds, @Pos, @NextPos - @Pos)));
                SET @ClaimId = CAST(@Item AS INT);
                
                -- Validate claim exists and is in Pending status
                IF NOT EXISTS (SELECT 1 FROM dbo.Claims WHERE ClaimId = @ClaimId)
                BEGIN
                    RAISERROR('Claim %d not found', 16, 1, @ClaimId);
                END
                
                IF NOT EXISTS (SELECT 1 FROM dbo.Claims WHERE ClaimId = @ClaimId AND Status = 'Pending')
                BEGIN
                    RAISERROR('Claim %d is not in Pending status', 16, 1, @ClaimId);
                END
                
                -- Update claim status using the existing procedure logic
                UPDATE dbo.Claims
                SET Status = 'Verified',
                    VerifiedAt = GETDATE()
                WHERE ClaimId = @ClaimId;
                
                -- Record status history
                INSERT INTO dbo.StatusHistory (EntityType, EntityId, Status, ChangedByUserId, Notes)
                VALUES ('Claim', @ClaimId, 'Verified', @UserId, 'Bulk verification');
                
                SET @VerifiedCount = @VerifiedCount + 1;
            END TRY
            BEGIN CATCH
                -- Rollback only this claim, continue with next
                ROLLBACK TRANSACTION Savepoint_BeforeClaim;
                SET @FailedCount = @FailedCount + 1;
                -- Continue processing other claims
            END CATCH
            
            SET @Pos = @NextPos + 1;
        END
        
        -- Log audit
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Claim', 'Bulk', 
                    'Bulk verified ' + CAST(@VerifiedCount AS NVARCHAR(10)) + ' claims, ' + 
                    CAST(@FailedCount AS NVARCHAR(10)) + ' failed');
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
END;
GO

-- Stored Procedure: Settle Claim with Multiple Payments (with savepoints)
-- Note: This assumes a Payments table exists. For demonstration, we'll create a simplified version.
CREATE PROCEDURE dbo.SP_SettleClaimWithPayments
    @ClaimId INT,
    @PaymentAmounts NVARCHAR(MAX), -- Comma-separated: "1000.00,500.00,250.00"
    @PaymentDates NVARCHAR(MAX) = NULL, -- Comma-separated dates (optional)
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
        -- Step 1: Validate and settle claim (CRITICAL - must succeed)
        SAVE TRANSACTION Savepoint_ClaimSettled;
        
        IF NOT EXISTS (SELECT 1 FROM dbo.Claims WHERE ClaimId = @ClaimId)
        BEGIN
            SET @ErrorMessage = 'Claim not found';
            ROLLBACK TRANSACTION;
            RETURN;
        END
        
        -- Update claim status
        UPDATE dbo.Claims
        SET Status = 'Settled',
            SettledAt = GETDATE()
        WHERE ClaimId = @ClaimId;
        
        -- Record status history
        INSERT INTO dbo.StatusHistory (EntityType, EntityId, Status, ChangedByUserId, Notes)
        VALUES ('Claim', @ClaimId, 'Settled', @UserId, 'Claim settled with payments');
        
        -- Step 2: Process payments (each can fail independently)
        DECLARE @PaymentAmount DECIMAL(18,2);
        DECLARE @PaymentDate DATE;
        DECLARE @Pos INT = 1;
        DECLARE @NextPos INT;
        DECLARE @Item NVARCHAR(50);
        DECLARE @PaymentCount INT = 0;
        DECLARE @FailedPaymentCount INT = 0;
        
        -- Process payment amounts
        WHILE @Pos <= LEN(@PaymentAmounts)
        BEGIN
            BEGIN TRY
                -- Create savepoint before each payment
                SAVE TRANSACTION Savepoint_BeforePayment;
                
                SET @NextPos = CHARINDEX(',', @PaymentAmounts, @Pos);
                IF @NextPos = 0 SET @NextPos = LEN(@PaymentAmounts) + 1;
                
                SET @Item = LTRIM(RTRIM(SUBSTRING(@PaymentAmounts, @Pos, @NextPos - @Pos)));
                SET @PaymentAmount = CAST(@Item AS DECIMAL(18,2));
                
                -- Validate payment amount
                IF @PaymentAmount <= 0
                BEGIN
                    RAISERROR('Payment amount must be positive', 16, 1);
                END
                
                -- Get payment date if provided
                IF @PaymentDates IS NOT NULL
                BEGIN
                    -- Parse date (simplified - in production use proper parsing)
                    SET @PaymentDate = CAST(GETDATE() AS DATE); -- Default to today
                END
                ELSE
                BEGIN
                    SET @PaymentDate = CAST(GETDATE() AS DATE);
                END
                
                -- Insert payment record (simplified - assumes Payments table structure)
                -- In production, this would insert into a Payments table
                -- For now, we'll create an audit log entry
                INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
                VALUES (@UserId, 'CREATE', 'Payment', CAST(@ClaimId AS NVARCHAR(100)),
                        'Payment of ' + CAST(@PaymentAmount AS NVARCHAR(20)) + ' recorded for claim ' + CAST(@ClaimId AS NVARCHAR(10)));
                
                SET @PaymentCount = @PaymentCount + 1;
            END TRY
            BEGIN CATCH
                -- Rollback only this payment, continue with next
                ROLLBACK TRANSACTION Savepoint_BeforePayment;
                SET @FailedPaymentCount = @FailedPaymentCount + 1;
                -- Continue processing other payments
            END CATCH
            
            SET @Pos = @NextPos + 1;
        END
        
        -- Step 3: Update asset status (CRITICAL - must succeed)
        DECLARE @AssetId INT;
        SELECT @AssetId = AssetId FROM dbo.Claims WHERE ClaimId = @ClaimId;
        
        -- Note: In production, you might update asset status here
        -- For now, we'll just log it
        
        -- Final audit log
        IF @UserId IS NOT NULL
        BEGIN
            INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
            VALUES (@UserId, 'UPDATE', 'Claim', CAST(@ClaimId AS NVARCHAR(100)),
                    'Claim settled with ' + CAST(@PaymentCount AS NVARCHAR(10)) + ' payments, ' + 
                    CAST(@FailedPaymentCount AS NVARCHAR(10)) + ' failed');
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
-- Stored Procedure: SP_CreateUserByAdmin
-- Purpose: Create a new user account - only allowed by Admin users
-- Security: Enforces admin-only user creation at database level
-- ============================================================================
CREATE PROCEDURE dbo.SP_CreateUserByAdmin
    @Username NVARCHAR(100),
    @PasswordHash VARBINARY(256),
    @Role NVARCHAR(50),
    @CreatedByUserId INT,  -- ID of admin user creating this account
    @Email NVARCHAR(200) = NULL,
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
        
        -- Create the user
        INSERT INTO dbo.Users (Username, PasswordHash, Role, Email, CreatedAt, IsActive)
        VALUES (@Username, @PasswordHash, @Role, @Email, SYSUTCDATETIME(), 1);
        
        SET @NewUserId = SCOPE_IDENTITY();
        
        -- Audit log entry
        INSERT INTO dbo.AuditLog (UserId, Action, Entity, EntityId, Details)
        VALUES (@CreatedByUserId, 'CREATE', 'User', CAST(@NewUserId AS NVARCHAR(100)),
                'User account created: ' + @Username + ' with role ' + @Role);
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE();
        ROLLBACK TRANSACTION;
    END CATCH
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
-- SECTION 8: SAMPLE DATA WITH TRANSACTIONS
-- ============================================================================

-- Transaction 1: Insert sample deceased persons
BEGIN TRANSACTION;
BEGIN TRY
    INSERT INTO dbo.Deceased (NationalId, FirstName, LastName, DateOfBirth, DateOfDeath) VALUES
    ('ID001', 'John', 'Smith', '1950-01-15', '2023-06-20'),
    ('ID002', 'Mary', 'Johnson', '1945-03-22', '2023-08-10'),
    ('ID003', 'Robert', 'Williams', '1960-07-08', '2023-09-15');
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 1: Sample deceased persons inserted successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 1 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Transaction 2: Insert institutions
BEGIN TRANSACTION;
BEGIN TRY
    INSERT INTO dbo.Institutions (Name, Type, Contact, Address, Phone) VALUES
    ('National Bank', 'Bank', 'support@nationalbank.example', '123 Main St', '555-0100'),
    ('State Insurance', 'Insurance', 'help@stateins.example', '456 Oak Ave', '555-0200'),
    ('Global Investments', 'Investment', 'info@globalinv.example', '789 Pine Rd', '555-0300'),
    ('City Credit Union', 'Bank', 'contact@citycu.example', '321 Elm St', '555-0400');
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 2: Institutions inserted successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 2 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Transaction 3: Insert assets (demonstrates referential integrity)
BEGIN TRANSACTION;
BEGIN TRY
    DECLARE @Deceased1 INT = (SELECT DeceasedId FROM dbo.Deceased WHERE NationalId = 'ID001');
    DECLARE @Deceased2 INT = (SELECT DeceasedId FROM dbo.Deceased WHERE NationalId = 'ID002');
    DECLARE @Inst1 INT = (SELECT InstitutionId FROM dbo.Institutions WHERE Name = 'National Bank');
    DECLARE @Inst2 INT = (SELECT InstitutionId FROM dbo.Institutions WHERE Name = 'State Insurance');
    DECLARE @Inst3 INT = (SELECT InstitutionId FROM dbo.Institutions WHERE Name = 'Global Investments');
    
    INSERT INTO dbo.Assets (DeceasedId, InstitutionId, AssetType, Identifier, EstimatedValue) VALUES
    (@Deceased1, @Inst1, 'Bank Account', 'ACC-001-12345', 50000.00),
    (@Deceased1, @Inst2, 'Insurance Policy', 'POL-001-67890', 100000.00),
    (@Deceased2, @Inst1, 'Bank Account', 'ACC-002-11111', 25000.00),
    (@Deceased2, @Inst3, 'Investment Account', 'INV-002-22222', 75000.00),
    (@Deceased2, @Inst2, 'Insurance Policy', 'POL-002-33333', 50000.00);
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 3: Assets inserted successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 3 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Transaction 4: Insert claimants and claims
BEGIN TRANSACTION;
BEGIN TRY
    DECLARE @Asset1 INT = (SELECT TOP 1 AssetId FROM dbo.Assets ORDER BY AssetId);
    DECLARE @Asset2 INT = (SELECT TOP 1 AssetId FROM dbo.Assets ORDER BY AssetId OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);
    
    INSERT INTO dbo.Claimants (NationalId, FirstName, LastName, Relationship, Contact, Email) VALUES
    ('CLM001', 'Jane', 'Smith', 'Spouse', 'jane.smith@email.com', 'jane.smith@email.com'),
    ('CLM002', 'Michael', 'Johnson', 'Son', 'michael.j@email.com', 'michael.j@email.com'),
    ('CLM003', 'Sarah', 'Williams', 'Daughter', 'sarah.w@email.com', 'sarah.w@email.com');
    
    DECLARE @Claimant1 INT = (SELECT ClaimantId FROM dbo.Claimants WHERE NationalId = 'CLM001');
    DECLARE @Claimant2 INT = (SELECT ClaimantId FROM dbo.Claimants WHERE NationalId = 'CLM002');
    
    INSERT INTO dbo.Claims (AssetId, ClaimantId, Status, Notes) VALUES
    (@Asset1, @Claimant1, 'Pending', 'Initial claim submission'),
    (@Asset2, @Claimant2, 'Pending', 'Awaiting verification documents');
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 4: Claimants and claims inserted successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 4 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Transaction 5: Insert sample users
BEGIN TRANSACTION;
BEGIN TRY
    INSERT INTO dbo.Users (Username, PasswordHash, Role, Email) VALUES
    ('admin', 0x41444D494E, 'Admin', 'admin@farvs.example'),
    ('staff1', 0x5354414646, 'Staff', 'staff1@farvs.example'),
    ('viewer1', 0x564945574552, 'Viewer', 'viewer1@farvs.example');
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 5: Sample users inserted successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 5 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Transaction 6: Seed Asset Types
BEGIN TRANSACTION;
BEGIN TRY
    IF NOT EXISTS (SELECT 1 FROM dbo.AssetTypes)
    BEGIN
        INSERT INTO dbo.AssetTypes (Name, Description) VALUES
        ('Bank Account', 'Checking, savings, and other bank accounts'),
        ('Investment', 'Stocks, bonds, mutual funds'),
        ('Insurance Policy', 'Life, health, and other insurance policies'),
        ('Real Estate', 'Property and land holdings'),
        ('Vehicle', 'Cars, boats, and other vehicles'),
        ('Retirement Account', '401k, IRA, pension accounts'),
        ('Digital Asset', 'Cryptocurrency, digital wallets'),
        ('Business Interest', 'Business ownership and partnerships'),
        ('Collectible', 'Art, antiques, collectibles');
    END
    
    COMMIT TRANSACTION;
    PRINT 'Transaction 6: Asset types seeded successfully';
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    PRINT 'Transaction 6 failed: ' + ERROR_MESSAGE();
END CATCH;
GO

-- ============================================================================
-- SECTION 9: DEMONSTRATION QUERIES (Show normalization and relationships)
-- ============================================================================

-- Query 1: Demonstrate normalization - Get deceased with all related data
-- This query shows how normalization allows efficient joins without data duplication
/*
SELECT 
    d.DeceasedId,
    d.FirstName + ' ' + d.LastName AS DeceasedName,
    COUNT(DISTINCT a.AssetId) AS AssetCount,
    SUM(a.EstimatedValue) AS TotalValue,
    COUNT(DISTINCT c.ClaimId) AS ClaimCount
FROM dbo.Deceased d
LEFT JOIN dbo.Assets a ON d.DeceasedId = a.DeceasedId
LEFT JOIN dbo.Claims c ON a.AssetId = c.AssetId
GROUP BY d.DeceasedId, d.FirstName, d.LastName;
*/

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
