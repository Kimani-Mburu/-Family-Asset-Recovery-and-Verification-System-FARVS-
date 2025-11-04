-- FARVS Database Schema
-- Run on Microsoft SQL Server

IF DB_ID('FARVS') IS NULL
BEGIN
    CREATE DATABASE FARVS;
END
GO

USE FARVS;
GO

-- Drop enterprise extension tables first (reverse dependencies)
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

CREATE TABLE dbo.Deceased (
    DeceasedId INT IDENTITY(1,1) PRIMARY KEY,
    NationalId VARCHAR(20) NULL,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    DateOfBirth DATE NULL,
    DateOfDeath DATE NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE UNIQUE INDEX IX_Deceased_NationalId ON dbo.Deceased(NationalId) WHERE NationalId IS NOT NULL;

CREATE TABLE dbo.Institutions (
    InstitutionId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(200) NOT NULL,
    Type NVARCHAR(100) NULL,
    Contact NVARCHAR(200) NULL
);

CREATE TABLE dbo.Assets (
    AssetId INT IDENTITY(1,1) PRIMARY KEY,
    DeceasedId INT NOT NULL,
    InstitutionId INT NOT NULL,
    AssetType NVARCHAR(100) NOT NULL,
    Identifier NVARCHAR(200) NULL,
    EstimatedValue DECIMAL(18,2) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Assets_Deceased FOREIGN KEY (DeceasedId) REFERENCES dbo.Deceased(DeceasedId) ON DELETE CASCADE,
    CONSTRAINT FK_Assets_Institution FOREIGN KEY (InstitutionId) REFERENCES dbo.Institutions(InstitutionId)
);

CREATE TABLE dbo.Claimants (
    ClaimantId INT IDENTITY(1,1) PRIMARY KEY,
    NationalId VARCHAR(20) NULL,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Relationship NVARCHAR(100) NULL,
    Contact NVARCHAR(200) NULL
);

CREATE UNIQUE INDEX IX_Claimants_NationalId ON dbo.Claimants(NationalId) WHERE NationalId IS NOT NULL;

CREATE TABLE dbo.Claims (
    ClaimId INT IDENTITY(1,1) PRIMARY KEY,
    AssetId INT NOT NULL,
    ClaimantId INT NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
    FiledAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    VerifiedAt DATETIME2 NULL,
    SettledAt DATETIME2 NULL,
    Notes NVARCHAR(1000) NULL,
    CONSTRAINT FK_Claims_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE,
    CONSTRAINT FK_Claims_Claimant FOREIGN KEY (ClaimantId) REFERENCES dbo.Claimants(ClaimantId)
);

-- ENTERPRISE EXTENSIONS

-- Users for RBAC (store password hashes, not plaintext)
CREATE TABLE dbo.Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARBINARY(256) NOT NULL,
    Role NVARCHAR(50) NOT NULL, -- e.g., Admin, Staff, Viewer
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    LastLoginAt DATETIME2 NULL
);

-- Audit log for changes and access
CREATE TABLE dbo.AuditLog (
    AuditId BIGINT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NULL,
    Action NVARCHAR(100) NOT NULL, -- CREATE/UPDATE/DELETE/ACCESS
    Entity NVARCHAR(100) NOT NULL, -- e.g., Deceased, Asset, Claim
    EntityId NVARCHAR(100) NULL,
    Details NVARCHAR(2000) NULL,
    IpAddress NVARCHAR(64) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_AuditLog_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
);

-- Asset types taxonomy (hierarchical)
CREATE TABLE dbo.AssetTypes (
    AssetTypeId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL UNIQUE,
    ParentAssetTypeId INT NULL,
    CONSTRAINT FK_AssetTypes_Parent FOREIGN KEY (ParentAssetTypeId) REFERENCES dbo.AssetTypes(AssetTypeId)
);

-- Time-series valuations for assets
CREATE TABLE dbo.AssetValuations (
    ValuationId BIGINT IDENTITY(1,1) PRIMARY KEY,
    AssetId INT NOT NULL,
    ValuationDate DATE NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    Source NVARCHAR(200) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_AssetValuations UNIQUE (AssetId, ValuationDate),
    CONSTRAINT FK_AssetValuations_Asset FOREIGN KEY (AssetId) REFERENCES dbo.Assets(AssetId) ON DELETE CASCADE
);

-- Status history for auditability (generic entity)
CREATE TABLE dbo.StatusHistory (
    StatusHistoryId BIGINT IDENTITY(1,1) PRIMARY KEY,
    EntityType NVARCHAR(50) NOT NULL, -- e.g., Claim, Case
    EntityId INT NOT NULL,
    Status NVARCHAR(50) NOT NULL,
    ChangedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ChangedByUserId INT NULL,
    Notes NVARCHAR(1000) NULL,
    CONSTRAINT FK_StatusHistory_User FOREIGN KEY (ChangedByUserId) REFERENCES dbo.Users(UserId)
);

-- Case management
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

CREATE TABLE dbo.Tasks (
    TaskId INT IDENTITY(1,1) PRIMARY KEY,
    CaseId INT NOT NULL,
    Title NVARCHAR(200) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending', -- Pending/In Progress/Done
    DueDate DATE NULL,
    AssignedToUserId INT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Tasks_Case FOREIGN KEY (CaseId) REFERENCES dbo.Cases(CaseId) ON DELETE CASCADE,
    CONSTRAINT FK_Tasks_User FOREIGN KEY (AssignedToUserId) REFERENCES dbo.Users(UserId)
);

CREATE TABLE dbo.Notes (
    NoteId BIGINT IDENTITY(1,1) PRIMARY KEY,
    CaseId INT NOT NULL,
    UserId INT NULL,
    Content NVARCHAR(2000) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Notes_Case FOREIGN KEY (CaseId) REFERENCES dbo.Cases(CaseId) ON DELETE CASCADE,
    CONSTRAINT FK_Notes_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
);

-- Attachments registry (store paths/URLs; actual files should be in blob storage or file server)
CREATE TABLE dbo.Attachments (
    AttachmentId BIGINT IDENTITY(1,1) PRIMARY KEY,
    EntityType NVARCHAR(50) NOT NULL, -- e.g., Case, Claim, Asset
    EntityId INT NOT NULL,
    FileName NVARCHAR(260) NOT NULL,
    MimeType NVARCHAR(100) NULL,
    Location NVARCHAR(500) NOT NULL, -- file path or URL
    UploadedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UploadedByUserId INT NULL,
    CONSTRAINT FK_Attachments_User FOREIGN KEY (UploadedByUserId) REFERENCES dbo.Users(UserId)
);

-- Minimal seed data for Institutions (optional for dev)
INSERT INTO dbo.Institutions (Name, Type, Contact) VALUES
('National Bank', 'Bank', 'support@nationalbank.example'),
('State Insurance', 'Insurance', 'help@stateins.example');

-- Seed core asset types
IF NOT EXISTS (SELECT 1 FROM dbo.AssetTypes)
BEGIN
    INSERT INTO dbo.AssetTypes (Name) VALUES
    ('Bank Account'),
    ('Investment'),
    ('Insurance Policy'),
    ('Real Estate'),
    ('Vehicle'),
    ('Retirement Account'),
    ('Digital Asset'),
    ('Business Interest'),
    ('Collectible');
END


