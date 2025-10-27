# Family Asset Recovery and Verification System (FARVS)

A comprehensive database system that enables families to trace, verify, and claim unclaimed assets of deceased relatives through a Python Tkinter interface connected to Microsoft SQL Server.

## 🎯 Project Overview

FARVS is a Database Systems Group Project that demonstrates:
- **Database Design**: Normalized relational database with proper relationships
- **Python Integration**: Tkinter GUI with pyodbc database connectivity
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Data Integrity**: Foreign key constraints and relationship management
- **User Interface**: Intuitive forms for managing deceased records, assets, claims, and reports

## 🏗️ System Architecture

```
[Tkinter UI Layer]
        ↓
[Python Logic & CRUD Modules]
        ↓
    (pyodbc)
        ↓
[SQL Server Database: FARVS]
    ├── Deceased
    ├── Assets
    ├── Institutions
    ├── Claimants
    └── Claims
```

## 📂 Project Structure

```
FARVS/
│
├── db/                          # Database layer
│   ├── __init__.py
│   ├── farvs_db.sql            # Database schema
│   ├── db_connect.py           # Connection utilities
│   ├── models_deceased.py      # Deceased records model
│   ├── models_assets.py        # Assets model
│   ├── models_claims.py        # Claims model
│   ├── models_claimants.py     # Claimants model
│   └── models_institutions.py # Institutions model
│
├── ui/                          # User interface layer
│   ├── __init__.py
│   ├── ui_deceased.py          # Deceased records UI
│   ├── ui_assets.py            # Assets management UI
│   ├── ui_claims.py            # Claims processing UI
│   └── ui_reports.py           # Reports and analytics UI
│
├── config.py                   # Configuration management
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── plan.md                    # Project plan and documentation
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Microsoft SQL Server** (Express or Full)
- **ODBC Driver 17 for SQL Server**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FARVS
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   - Open SQL Server Management Studio
   - Run the `db/farvs_db.sql` script to create the database and tables

4. **Configure the connection**
   ```bash
   cp .env.example .env
   # Edit .env with your SQL Server connection details
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# SQL Server Connection Settings
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost\\SQLEXPRESS
DB_NAME=FARVS
DB_TRUSTED_CONNECTION=yes

# Alternative: SQL Server Authentication
# DB_USERNAME=your_username
# DB_PASSWORD=your_password
```

### Database Setup

The `db/farvs_db.sql` script creates:
- **FARVS** database
- **5 main tables** with proper relationships:
  - `Deceased`: Deceased person records
  - `Institutions`: Financial institutions
  - `Assets`: Assets linked to deceased persons
  - `Claimants`: People claiming assets
  - `Claims`: Claims linking assets to claimants

## 🎮 Usage

### Main Application

Launch the application with `python main.py` to access:

1. **Dashboard**: System overview and navigation
2. **Deceased Records**: Manage deceased person information
3. **Asset Management**: Link assets to deceased persons
4. **Claims Processing**: Handle claims and claimants
5. **Reports & Analytics**: Generate reports and view statistics

### Key Features

- **Data Validation**: Input validation and error handling
- **Search & Filter**: Find records quickly
- **CRUD Operations**: Full create, read, update, delete functionality
- **Relationship Management**: Maintain data integrity
- **Export Functionality**: Export reports to CSV
- **Status Tracking**: Track claim processing workflow

## 🧪 Testing

### Database Connection Test

```python
from db.db_connect import try_connect

success, error = try_connect()
if success:
    print("Database connection successful!")
else:
    print(f"Connection failed: {error}")
```

### Sample Data

The system includes placeholder data for demonstration. Replace the TODO comments in the UI modules with actual database calls to connect to real data.

## 📊 Database Schema

### Entity Relationships

- **One Deceased** → **Many Assets**
- **One Institution** → **Many Assets**
- **One Asset** → **Many Claims**
- **One Claimant** → **Many Claims**

### Key Constraints

- Foreign key relationships ensure data integrity
- Cascade deletes maintain referential integrity
- Unique indexes on National IDs prevent duplicates
- Default values for timestamps and status fields

## 🔧 Development

### Adding New Features

1. **Database Changes**: Update `farvs_db.sql` and run migration
2. **Model Updates**: Modify appropriate model in `db/models_*.py`
3. **UI Changes**: Update corresponding UI module in `ui/ui_*.py`
4. **Integration**: Test the complete workflow

### Code Structure

- **Models**: Handle all database operations with proper error handling
- **UI Modules**: Provide user-friendly interfaces with validation
- **Configuration**: Centralized settings management
- **Documentation**: Comprehensive comments and docstrings

## 📝 Project Deliverables

1. **ER Diagram**: Database relationship visualization
2. **SQL Schema**: Complete database structure (`farvs_db.sql`)
3. **Python Application**: Full Tkinter interface with database connectivity
4. **Documentation**: Comprehensive setup and usage instructions
5. **Testing**: Database connection and functionality validation

## 🤝 Contributing

This is a group project with defined roles:

- **Database Lead**: Schema design and connection setup
- **Deceased Records Developer**: Deceased records management
- **Assets Module Developer**: Asset management and relationships
- **Claims Module Developer**: Claims processing and workflow
- **Reports & Integration Developer**: Analytics and system integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify SQL Server is running
   - Check connection string in `.env`
   - Ensure ODBC Driver 17 is installed

2. **Import Errors**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and module structure

3. **Database Schema Issues**
   - Re-run `farvs_db.sql` to recreate tables
   - Check for existing database conflicts

### Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the code comments and documentation
3. Verify database connectivity and configuration

---

**Developed for Database Systems Group Project**  
*Python + Tkinter + Microsoft SQL Server*
