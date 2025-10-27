-- FARVS Database Schema
-- Run on Microsoft SQL Server

IF DB_ID('FARVS') IS NULL
BEGIN
    CREATE DATABASE FARVS;
END
GO

USE FARVS;
GO

-- Drop tables in reverse dependency order (for idempotency during development)
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

-- Minimal seed data for Institutions (optional for dev)
INSERT INTO dbo.Institutions (Name, Type, Contact) VALUES
('National Bank', 'Bank', 'support@nationalbank.example'),
('State Insurance', 'Insurance', 'help@stateins.example');


