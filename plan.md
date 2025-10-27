# Family Asset Recovery and Verification System (FARVS)
### Database Systems Group Project — Python (Tkinter) + MSSQL

---

## 🧩 Project Overview

**Project Title:** Family Asset Recovery and Verification System (FARVS)  
**Goal:** To design and implement a database system that enables families to trace, verify, and claim unclaimed assets of deceased relatives — integrating a functional Python Tkinter interface with a Microsoft SQL Server database.

**Core Focus:**  
- Database Design (ERD, Normalization, Relationships)  
- Python Database Connectivity (using `pyodbc`)  
- CRUD Operations through Tkinter GUI  
- Group Collaboration and Division of Work  

---

## 🎯 Project Objectives

1. Design a normalized relational database for managing deceased persons, their assets, and claims.  
2. Implement a user-friendly Tkinter interface that performs CRUD operations.  
3. Connect Python to MS SQL Server using `pyodbc`.  
4. Demonstrate relational queries and data integrity through linked modules.  
5. Promote teamwork in database design, coding, and documentation.

---

## 👥 Group Roles and Coding Responsibilities

Each member contributes to **both database and Python coding** through separate modules that integrate into one final system.

| Member | Role | Coding Focus | Responsibilities |
|--------|------|---------------|------------------|
| **1. Database Lead / Setup Developer** | Database creation and connection setup | Schema + utility functions | - Write SQL schema (`farvs_db.sql`).<br>- Create database connection module (`db_connect.py`).<br>- Ensure all tables and constraints exist.<br>- Generate sample data for testing. |
| **2. Deceased Records Developer** | Manage Deceased table | CRUD + Tkinter form | - Build Tkinter window for adding, editing, and deleting deceased records.<br>- Write SQL operations in `models_deceased.py`.<br>- Create "View All Deceased" feature using Tkinter Treeview. |
| **3. Assets Module Developer** | Manage Assets table | CRUD + Joins | - Develop form for adding assets linked to deceased persons.<br>- Implement SQL joins between Deceased and Assets.<br>- Display assets per deceased person. |
| **4. Claims Module Developer** | Manage Claimants and Claims | CRUD + Relationship handling | - Create forms for Claimants and Claims.<br>- Link claims to both assets and claimants.<br>- Implement update of claim status (Pending, Verified, Settled). |
| **5. Reports & Integration Developer** | Combine all modules + reporting | Dashboard + reports | - Create main dashboard and navigation interface (`main.py`).<br>- Implement search and reporting (pending claims, total assets, etc.).<br>- Integrate all modules and handle final testing. |

---

## 🧱 System Architecture
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

---

## 📂 Project Folder Structure
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
└── README.md                  # Comprehensive setup guide
```

---

## 🧠 Technical Details

### Database:
- **Platform:** Microsoft SQL Server  
- **Database Name:** `FARVS`  
- **Key Tables:** Deceased, Assets, Institutions, Claimants, Claims  
- **Normalization:** 3NF  
- **Relations:**  
  - One Deceased → Many Assets  
  - One Claimant → Many Claims  
  - One Asset → One Institution  
  - One Claim → One Asset  

### Python:
- **Version:** Python 3.10+  
- **Libraries:** `pyodbc`, `python-dotenv`, `tkinter` (built-in)  
- **Configuration:** Environment-based configuration with `.env` file
- **Connection Management:** Centralized connection utilities with error handling
- **Code Quality:** Comprehensive comments, type hints, and error handling

---

## 🗓️ Work Plan (5 Weeks)

| Week | Focus | Active Members | Deliverables |
|------|-------|----------------|--------------|
| Week 1 | Planning and role assignment | All | Defined roles, finalized schema plan |
| Week 2 | Database design and ERD creation | 1, 2 | ER Diagram + SQL schema |
| Week 3 | Implement backend (CRUD + connection) | 2, 3, 4 | Working database logic |
| Week 4 | Tkinter UI creation and linking | 2, 3, 4, 5 | UI windows connected to DB |
| Week 5 | Testing, integration, and report writing | All | Final report, screenshots, demo |

---

## 📦 Deliverables Summary

1. **ER Diagram** showing relationships between tables.

2. **SQL Script** (`farvs_db.sql`) for creating and populating database.

3. **Python Application** (Tkinter UI + pyodbc connection) with:
   - Complete CRUD operations for all entities
   - Data validation and error handling
   - Search and filtering capabilities
   - Export functionality (CSV)
   - Comprehensive reporting system

4. **Documentation:**
   - Comprehensive README with setup instructions
   - Code comments and docstrings throughout
   - Configuration management with environment variables
   - Troubleshooting guide

5. **Project Structure:**
   - Modular design with separate UI and database layers
   - Proper Python package structure with `__init__.py` files
   - Environment-based configuration
   - Dependencies management with `requirements.txt`

6. **Screenshots / Demo Video** showing working system.

7. **Final Report Document:**
   - Problem Statement & Objectives
   - ER Diagram & Data Model
   - SQL Schema & Queries
   - Tkinter Interface Overview
   - Test Results & Future Work

---

## 💡 Implemented Enhancements

✅ **Comprehensive Documentation**: Complete README with setup instructions and troubleshooting  
✅ **Configuration Management**: Environment-based configuration with `.env` file support  
✅ **Error Handling**: Robust error handling throughout the application  
✅ **Data Validation**: Input validation and user feedback  
✅ **Search & Filtering**: Advanced search capabilities across all modules  
✅ **Export Functionality**: CSV export for reports  
✅ **Modular Architecture**: Clean separation between UI and database layers  
✅ **Type Hints**: Python type annotations for better code quality  
✅ **Code Comments**: Comprehensive documentation throughout the codebase  

## 🚀 Additional Enhancements (for bonus marks)

- Add user login with roles (admin, staff)
- Include asset search by keyword or date range
- Generate summary reports (total claimed assets, pending cases)
- Use stored procedures or views for advanced database logic
- Add data visualization charts (matplotlib integration)
- Implement audit logging for data changes
- Add backup and restore functionality