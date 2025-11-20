# Family Asset Recovery and Verification System (FARVS)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-red.svg)](https://www.microsoft.com/sql-server)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive database system that enables families to trace, verify, and claim unclaimed assets of deceased relatives through a Python Tkinter interface connected to Microsoft SQL Server.

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Database Design](#-database-design)
- [Security](#-security)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [License](#-license)

## ✨ Features

- **Complete CRUD Operations**: Full Create, Read, Update, Delete functionality for all entities
- **Database-Centric Architecture**: All business logic in stored procedures, triggers, and views
- **Normalized Database Design**: Third Normal Form (3NF) with proper relationships
- **Transaction Management**: ACID-compliant transactions with savepoints for partial rollbacks
- **Advanced Database Components**: 22+ stored procedures, 5 triggers, 5 views
- **Role-Based Access Control**: Admin, Staff, and Viewer roles with database-level authentication
- **SQL Server Login Integration**: Automatic SQL Server login creation with role-based permissions
- **Onboarding System**: First-time setup with automatic admin account creation
- **Asset Normalization**: Type-specific asset detail tables (Bank Account, Vehicle, Real Estate, Investment, Insurance)
- **Audit Logging**: Comprehensive tracking of all user actions
- **Modern UI**: Professional blue and white themed interface with scrollable forms and card/table views
- **Data Validation**: Input validation at both application and database levels
- **Secure Authentication**: SHA-256 password hashing with salt

## 🏗️ System Architecture

```
┌─────────────────────────────────────┐
│   Tkinter UI Layer                  │
│   (Blue & White Theme)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Python Application Layer          │
│   - Models (CRUD Operations)        │
│   - UI Components                   │
│   - Authentication                  │
└──────────────┬──────────────────────┘
               │
               │ (pyodbc)
               ▼
┌─────────────────────────────────────┐
│   Microsoft SQL Server Database     │
│   - Tables (12, normalized 3NF)    │
│   - Stored Procedures (7)          │
│   - Triggers (5)                   │
│   - Views (5)                       │
│   - Indexes & Constraints          │
└─────────────────────────────────────┘
```

## 📦 Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Microsoft SQL Server** (Express or Full Edition)
- **ODBC Driver 17 for SQL Server** ([Download](https://docs.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server))
- **Git** (for cloning the repository)

## 🚀 Installation

### Step 1: Clone the Repository

   ```bash
git clone https://github.com/Kimani-Mburu/-Family-Asset-Recovery-and-Verification-System-FARVS-.git
cd -Family-Asset-Recovery-and-Verification-System-FARVS-
   ```

### Step 2: Install Python Dependencies

   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Set Up the Database

1. Open **SQL Server Management Studio (SSMS)**
2. Connect to your SQL Server instance
3. Open and execute `db/farvs_db.sql`
4. The script will create:
   - FARVS database
   - 12 tables with relationships
   - 7 stored procedures
   - 5 triggers
   - 5 views
   - Indexes and constraints
   - Sample data (optional)

### Step 4: Configure Environment

Create a `.env` file in the project root:

```env
# SQL Server Connection Settings
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=FARVS
DB_TRUSTED_CONNECTION=yes

# Alternative: SQL Server Authentication
# DB_USERNAME=your_username
# DB_PASSWORD=your_password

# Optional: Encryption Settings
DB_ENCRYPT=yes
DB_TRUST_SERVER_CERTIFICATE=yes

# Optional: Debug Logging
DEBUG=false
```

### Step 5: Seed Database (Optional)

```bash
python db/seed_data.py
```

This creates sample users:
- **Admin**: `admin` / `admin123`
- **Staff**: `staff` / `staff123`

### Step 6: Run the Application

```bash
python main.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_DRIVER` | ODBC Driver name | Yes | `ODBC Driver 17 for SQL Server` |
| `DB_SERVER` | SQL Server instance | Yes | - |
| `DB_NAME` | Database name | Yes | `FARVS` |
| `DB_TRUSTED_CONNECTION` | Use Windows Authentication | No | `yes` |
| `DB_USERNAME` | SQL Server username | No* | - |
| `DB_PASSWORD` | SQL Server password | No* | - |
| `DB_ENCRYPT` | Enable encryption | No | `yes` |
| `DEBUG` | Enable debug logging | No | `false` |

*Required if `DB_TRUSTED_CONNECTION=no`

### Connection String Examples

**Windows Authentication:**
```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=FARVS
DB_TRUSTED_CONNECTION=yes
```

**SQL Server Authentication:**
```env
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=FARVS
DB_TRUSTED_CONNECTION=no
DB_USERNAME=sa
DB_PASSWORD=YourPassword123
```

## 🎮 Usage

### Starting the Application

```bash
python main.py
```

### First-Time Setup (Onboarding)

On first launch, the application will show both "Sign In" and "Create Account" buttons:

1. Click **"Create Account"** to create the first administrator account
2. The first account automatically receives **Admin** privileges
3. After creation, you'll be automatically logged in
4. Subsequent launches will only show "Sign In" - only admins can create new users

### Default Login Credentials

After seeding the database (if using seed script):

- **Admin User**: `admin` / `admin123`
- **Staff User**: `staff` / `staff123`

### Main Features

1. **Deceased Records Management**
   - Add, edit, delete deceased person records
   - Search and filter records
   - View in table or card format

2. **Asset Management**
   - Link assets to deceased persons
   - Track asset values and institutions
   - Manage asset types and valuations

3. **Claims Processing**
   - Create claims for assets
   - Track claim status (Pending → Verified → Settled)
   - Manage claimants and relationships
   - View progress timeline

4. **Reports & Analytics**
   - System statistics dashboard
   - Generate reports (CSV export)
   - Filter by date range and status

### Using Stored Procedures

The application uses a database-centric architecture where all operations go through stored procedures:

```python
from db.db_operations import db_ops

# Create claim with validation
success, claim_id, error = db_ops.create_claim_with_validation(
    asset_id=1,
    claimant_id=1,
    status='Pending',
    notes='Initial claim',
    user_id=current_user['UserId']
)

# Update claim status
success, error = db_ops.update_claim_status(
    claim_id=claim_id,
    new_status='Verified',
    notes='Documents verified',
    user_id=current_user['UserId']
)

# Get data using views
claims = db_ops.get_all_claims_detailed()
```

## 🗄️ Database Design

### Normalization

The database follows **Third Normal Form (3NF)**:

- **1NF**: Each table has a primary key, atomic values, no repeating groups
- **2NF**: All non-key attributes fully dependent on primary key
- **3NF**: No transitive dependencies

### Database Components

| Component | Count | Purpose |
|-----------|-------|---------|
| **Tables** | 17 | Core data storage (normalized 3NF with asset detail tables) |
| **Stored Procedures** | 22+ | Business logic, validation, transactions, user management |
| **Triggers** | 5 | Automatic actions, audit logging |
| **Views** | 5 | Simplified queries, reporting |
| **Indexes** | 20+ | Performance optimization |
| **Constraints** | 15+ | Data integrity (PKs, FKs, checks) |

### Stored Procedures

**Deceased Operations:**
- SP_CreateDeceasedWithValidation, SP_UpdateDeceasedRecord, SP_DeleteDeceasedRecord, SP_GetDeceasedWithAssets

**Asset Operations:**
- SP_CreateAssetWithValidation, SP_UpdateAssetRecord, SP_DeleteAssetRecord, SP_GetAssetsByDeceased

**Claimant Operations:**
- SP_CreateClaimantWithValidation, SP_UpdateClaimantRecord, SP_DeleteClaimantRecord

**Claim Operations:**
- SP_CreateClaimWithValidation, SP_UpdateClaimStatus, SP_GetPendingClaims

**Institution Operations:**
- SP_CreateInstitution, SP_UpdateInstitution, SP_DeleteInstitution

**User Management:**
- SP_CreateUserByAdmin, SP_UpdateUserByAdmin, SP_DeleteUserByAdmin, SP_GetAllUsers
- SP_CreateSQLServerLogin, SP_UpdateSQLServerLoginPermissions, SP_DropSQLServerLogin

### Triggers

1. **TR_Claims_StatusChange** - Auto-update timestamps on status change
2. **TR_Assets_AfterInsert** - Auto-log asset creation
3. **TR_Deceased_AfterUpdate** - Auto-log deceased updates
4. **TR_Claims_PreventInvalidStatus** - Prevent invalid status transitions
5. **TR_Claims_AutoCloseCase** - Auto-close case when all claims settled

### Views

1. **VW_Claims_Detailed** - Comprehensive claim information with joins
2. **VW_Assets_Summary** - Asset summary with claim counts
3. **VW_Deceased_WithAssets** - Deceased records with asset statistics
4. **VW_Claimants_WithClaims** - Claimants with claim statistics
5. **VW_System_Statistics** - System-wide statistics

### Transactions and Savepoints

The database implements ACID-compliant transactions with savepoints for partial rollbacks:

- **Batch Operations**: Savepoints allow partial success in batch operations
- **Error Recovery**: Failed operations can rollback to savepoints without affecting entire transaction
- **Complex Workflows**: Multi-step operations use transactions for atomicity

## 🔒 Security

### Implemented Security Features

✅ **Password Security**
- SHA-256 hashing with random 32-byte salt
- Constant-time password comparison
- Secure storage (VARBINARY in database)

✅ **SQL Injection Prevention**
- All queries use parameterized statements
- No string concatenation in SQL
- Stored procedures with parameter validation

✅ **Access Control**
- Role-based access control (Admin, Staff, Viewer)
- Database-level SQL Server login integration
- Automatic SQL Server login creation with role-based permissions
- Admin-only user creation (UI + Database level)
- Database-level role validation
- First-time onboarding with automatic admin assignment

✅ **Data Integrity**
- Primary keys on all tables
- Foreign key constraints with CASCADE
- Check constraints for data validation
- Unique constraints on critical fields

✅ **Audit Logging**
- Complete audit trail of all actions
- Tracks: UserId, Action, Entity, EntityId, Details, Timestamp, IP
- Automatic logging via triggers

✅ **Encryption**
- SSL/TLS encryption in transit
- Secure connection string configuration

### Security Best Practices

- Never commit `.env` file to version control
- Use strong passwords for database accounts
- Regularly review audit logs
- Keep SQL Server updated with latest security patches
- Use Windows Authentication when possible

## 💻 Development

### Project Structure

```
FARVS/
├── auth/                    # Authentication module
│   ├── password.py         # Password hashing
│   └── session.py          # Session management
│
├── db/                      # Database layer
│   ├── farvs_db.sql       # Complete database schema (ALL SQL)
│   ├── db_connect.py      # Connection utilities
│   ├── db_operations.py   # Database operations (stored procedure calls)
│   ├── models_*.py        # Database models (legacy, being phased out)
│   └── seed_data.py       # Database seeding
│
├── ui/                      # User interface layer
│   ├── theme.py           # Blue & white theme
│   ├── components.py      # Reusable UI components
│   ├── modals.py          # Modal dialogs
│   ├── scrollable_frame.py # Scrollable containers
│   └── ui_*.py            # UI modules
│
├── tests/                   # Test suite
│   ├── test_runner.py     # Test runner
│   ├── test_database_models.py
│   └── test_ui_components.py
│
├── config.py               # Configuration management
├── logging_config.py       # Logging configuration
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Database-Centric Architecture

FARVS follows a **database-centric architecture** where:

- **All SQL code** is in `db/farvs_db.sql` (stored procedures, triggers, views)
- **Python code** (`db/db_operations.py`) only calls stored procedures
- **No direct SQL** in Python models
- **Business logic** is in the database
- **Validation** happens at database level

### Adding New Features

1. **Database Changes**
   - Add stored procedures to `db/farvs_db.sql`
   - Add triggers if needed for automatic actions
   - Create views for complex queries

2. **Python Updates**
   - Add methods to `db/db_operations.py` to call new stored procedures
   - Update UI modules to use new operations

3. **UI Changes**
   - Update corresponding UI module in `ui/ui_*.py`
   - Maintain blue and white theme consistency

### Code Standards

- **Type Hints**: All functions have type annotations
- **Docstrings**: Comprehensive documentation for all modules, classes, and functions
- **Error Handling**: Comprehensive error handling throughout
- **Logging**: Use `logging_config.get_logger()` for all logging

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python tests/test_runner.py

# Run specific test modules
python -m unittest tests.test_database_models
python -m unittest tests.test_ui_components
```

### Test Coverage

- **Database Models**: CRUD operations for all models
- **UI Components**: Modal dialogs, date pickers, status badges
- **Data Validation**: Input validation and error handling
- **Database Operations**: Connection management and query execution

### Manual Testing

1. **Authentication**: Login, logout, user creation (admin only)
2. **Deceased Records**: Add, edit, delete, search, filter
3. **Assets**: Create, link to deceased, update, delete
4. **Claims**: Create, update status, track progress
5. **Reports**: Generate reports, export to CSV

### Database Connection Test

```python
from db.db_connect import try_connect

success, error = try_connect()
if success:
    print("✅ Database connection successful!")
else:
    print(f"❌ Connection failed: {error}")
```

## 🆘 Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify SQL Server is running
- Check connection string in `.env`
- Ensure ODBC Driver 17 is installed
- Test connection: `python -c "from db.db_connect import try_connect; print(try_connect())"`

**Import Errors**
- Verify dependencies: `pip install -r requirements.txt`
- Check Python path and module structure
- Ensure you're in the project root directory

**Database Schema Issues**
- Re-run `db/farvs_db.sql` to recreate tables
- Check for existing database conflicts
- Verify all stored procedures and triggers are created

**UI Not Displaying Correctly**
- Check for Tkinter/ttk compatibility issues
- Verify all UI modules are imported correctly
- Ensure theme is properly applied

**Stored Procedure Errors**
- Check parameter types match
- Verify OUTPUT parameters are properly handled
- Review error messages in stored procedure

### Debug Logging

Enable debug logging to troubleshoot issues:

```bash
# Windows PowerShell
$env:DEBUG="true"
python main.py

# Windows CMD
set DEBUG=true
python main.py

# Linux/Mac
export DEBUG=true
python main.py

# Or add to .env file
DEBUG=true
```

Debug logs include:
- Login attempts and results
- Password verification steps
- Database operations
- Error details with full tracebacks

## 📝 Logging

### Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (exceptions, failures)

### Using Logging in Code

```python
from logging_config import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include exception traceback
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a Database Systems Group Project demonstrating:
- Database design and normalization
- Python database connectivity
- CRUD operations through GUI
- Advanced database features (stored procedures, triggers, views)
- Transaction management and savepoints

## 📚 Additional Resources

- **Database Schema**: See `db/farvs_db.sql` for complete database structure
- **API Documentation**: All stored procedures are documented in `farvs_db.sql`
- **Code Documentation**: All Python modules include comprehensive docstrings

---

**Developed for Database Systems Group Project**  
*Python + Tkinter + Microsoft SQL Server*
