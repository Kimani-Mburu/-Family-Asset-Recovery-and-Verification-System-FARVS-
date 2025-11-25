"""
Comprehensive Database Seed Script for FARVS
Populates database with extensive sample data showcasing different scenarios

Scenarios included:
- High-value estates
- Multiple assets per deceased
- Various asset types (Bank, Insurance, Investment, Real Estate, Vehicle)
- Different claim statuses
- Multiple claimants per asset
- Various relationships
- Different institutions

Usage:
    python db/seed_comprehensive_data.py
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_connect import get_connection
from db.db_operations import db_ops
from db.models_deceased import DeceasedModel
from db.models_institutions import InstitutionsModel
from db.models_assets import AssetsModel
from db.models_claimants import ClaimantsModel
from db.models_claims import ClaimsModel
from db.models_users import UsersModel
from auth.password import hash_password
from auth.session import set_current_user

def create_users():
    """Create multiple users with different roles"""
    print("=" * 60)
    print("CREATING USERS")
    print("=" * 60)
    
    users_model = UsersModel()
    users_data = [
        {"username": "admin", "password": "admin123", "role": "Admin"},
        {"username": "staff1", "password": "staff123", "role": "Staff"},
        {"username": "staff2", "password": "staff123", "role": "Staff"},
        {"username": "viewer1", "password": "viewer123", "role": "Viewer"},
    ]
    
    created_users = {}
    for user_data in users_data:
        try:
            password_hash = hash_password(user_data["password"])
            user_id = users_model.create(user_data["username"], password_hash, user_data["role"])
            created_users[user_data["username"]] = user_id
            print(f"  ✅ Created {user_data['role']}: {user_data['username']} (ID: {user_id}) - Password: {user_data['password']}")
        except Exception as e:
            if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
                print(f"  ⚠️  {user_data['username']} already exists")
            else:
                print(f"  ❌ Error creating {user_data['username']}: {e}")
    
    return created_users

def create_institutions():
    """Create various types of institutions"""
    print("\n" + "=" * 60)
    print("CREATING INSTITUTIONS")
    print("=" * 60)
    
    institutions_model = InstitutionsModel()
    institutions_data = [
        # Banks
        {"Name": "First National Bank", "Type": "Bank", "Contact": "contact@fnb.com", "Address": "123 Main Street, City", "Phone": "555-0100"},
        {"Name": "Metro Savings Bank", "Type": "Bank", "Contact": "help@metrosavings.com", "Address": "456 Oak Avenue, City", "Phone": "555-0200"},
        {"Name": "City Credit Union", "Type": "Bank", "Contact": "info@citycu.com", "Address": "789 Pine Road, City", "Phone": "555-0300"},
        {"Name": "Regional Commercial Bank", "Type": "Bank", "Contact": "support@rcb.com", "Address": "321 Elm Street, City", "Phone": "555-0400"},
        
        # Insurance Companies
        {"Name": "ABC Insurance Company", "Type": "Insurance", "Contact": "info@abcinsurance.com", "Address": "654 Insurance Blvd, City", "Phone": "555-0500"},
        {"Name": "State Life Insurance", "Type": "Insurance", "Contact": "claims@statelife.com", "Address": "987 Life Avenue, City", "Phone": "555-0600"},
        {"Name": "Premier Health Insurance", "Type": "Insurance", "Contact": "service@premierhealth.com", "Address": "147 Health Way, City", "Phone": "555-0700"},
        
        # Investment Firms
        {"Name": "XYZ Investment Group", "Type": "Investment", "Contact": "support@xyzinvest.com", "Address": "258 Investment Plaza, City", "Phone": "555-0800"},
        {"Name": "Global Wealth Management", "Type": "Investment", "Contact": "info@globalwealth.com", "Address": "369 Wealth Street, City", "Phone": "555-0900"},
        {"Name": "Capital Markets Inc", "Type": "Investment", "Contact": "contact@capitalmarkets.com", "Address": "741 Capital Drive, City", "Phone": "555-1000"},
        
        # Real Estate
        {"Name": "Metro Property Management", "Type": "Real Estate", "Contact": "info@metropm.com", "Address": "852 Property Lane, City", "Phone": "555-1100"},
        {"Name": "Heritage Realty Group", "Type": "Real Estate", "Contact": "sales@heritagerealty.com", "Address": "963 Heritage Court, City", "Phone": "555-1200"},
    ]
    
    institution_ids = []
    for inst_data in institutions_data:
        try:
            inst_id = institutions_model.create(inst_data)
            institution_ids.append(inst_id)
            print(f"  ✅ {inst_data['Type']}: {inst_data['Name']} (ID: {inst_id})")
        except Exception as e:
            print(f"  ⚠️  Error creating {inst_data['Name']}: {e}")
    
    return institution_ids

def create_deceased_records():
    """Create diverse deceased records with different scenarios"""
    print("\n" + "=" * 60)
    print("CREATING DECEASED RECORDS")
    print("=" * 60)
    
    deceased_model = DeceasedModel()
    
    # Scenario 1: High-value estate (multiple assets)
    deceased_data = [
        # High-value estate - Business owner
        {
            "NationalId": "100100100",
            "FirstName": "Robert",
            "MiddleName": "James",
            "LastName": "Anderson",
            "Gender": "Male",
            "DateOfBirth": "1940-03-15",
            "DateOfDeath": "2023-01-20",
            "PlaceOfBirth": "New York, USA",
            "PlaceOfDeath": "New York, USA",
            "Address": "1000 Park Avenue, New York, NY 10021",
            "Occupation": "Business Executive",
            "MaritalStatus": "Married",
            "NextOfKin": "Margaret Anderson (Spouse)",
            "DeathCertificateNumber": "DC-2023-001",
            "Notes": "High-value estate with multiple assets. Business owner with extensive portfolio."
        },
        
        # Scenario 2: Retired professional - moderate assets
        {
            "NationalId": "200200200",
            "FirstName": "Margaret",
            "MiddleName": "Elizabeth",
            "LastName": "Thompson",
            "Gender": "Female",
            "DateOfBirth": "1945-07-22",
            "DateOfDeath": "2023-02-14",
            "PlaceOfBirth": "Boston, USA",
            "PlaceOfDeath": "Boston, USA",
            "Address": "2500 Beacon Street, Boston, MA 02108",
            "Occupation": "Retired Teacher",
            "MaritalStatus": "Widowed",
            "NextOfKin": "David Thompson (Son)",
            "DeathCertificateNumber": "DC-2023-002",
            "Notes": "Retired educator with pension and savings accounts."
        },
        
        # Scenario 3: Young professional - unexpected death
        {
            "NationalId": "300300300",
            "FirstName": "Michael",
            "MiddleName": "David",
            "LastName": "Chen",
            "Gender": "Male",
            "DateOfBirth": "1985-11-08",
            "DateOfDeath": "2023-03-10",
            "PlaceOfBirth": "San Francisco, USA",
            "PlaceOfDeath": "San Francisco, USA",
            "Address": "500 Market Street, San Francisco, CA 94105",
            "Occupation": "Software Engineer",
            "MaritalStatus": "Single",
            "NextOfKin": "Lisa Chen (Sister)",
            "DeathCertificateNumber": "DC-2023-003",
            "Notes": "Young professional with investment accounts and life insurance."
        },
        
        # Scenario 4: Elderly with long-term investments
        {
            "NationalId": "400400400",
            "FirstName": "Eleanor",
            "MiddleName": "Rose",
            "LastName": "Martinez",
            "Gender": "Female",
            "DateOfBirth": "1935-05-30",
            "DateOfDeath": "2023-04-05",
            "PlaceOfBirth": "Los Angeles, USA",
            "PlaceOfDeath": "Los Angeles, USA",
            "Address": "7500 Sunset Boulevard, Los Angeles, CA 90046",
            "Occupation": "Retired Nurse",
            "MaritalStatus": "Divorced",
            "NextOfKin": "Carlos Martinez (Son)",
            "DeathCertificateNumber": "DC-2023-004",
            "Notes": "Long-term investments and retirement accounts."
        },
        
        # Scenario 5: Real estate owner
        {
            "NationalId": "500500500",
            "FirstName": "William",
            "MiddleName": "Thomas",
            "LastName": "Johnson",
            "Gender": "Male",
            "DateOfBirth": "1950-09-12",
            "DateOfDeath": "2023-05-18",
            "PlaceOfBirth": "Chicago, USA",
            "PlaceOfDeath": "Chicago, USA",
            "Address": "1200 Michigan Avenue, Chicago, IL 60611",
            "Occupation": "Real Estate Developer",
            "MaritalStatus": "Married",
            "NextOfKin": "Patricia Johnson (Spouse)",
            "DeathCertificateNumber": "DC-2023-005",
            "Notes": "Real estate holdings and property investments."
        },
        
        # Scenario 6: Multiple bank accounts
        {
            "NationalId": "600600600",
            "FirstName": "Patricia",
            "MiddleName": "Ann",
            "LastName": "Williams",
            "Gender": "Female",
            "DateOfBirth": "1955-12-25",
            "DateOfDeath": "2023-06-22",
            "PlaceOfBirth": "Miami, USA",
            "PlaceOfDeath": "Miami, USA",
            "Address": "3000 Ocean Drive, Miami, FL 33139",
            "Occupation": "Accountant",
            "MaritalStatus": "Married",
            "NextOfKin": "Richard Williams (Spouse)",
            "DeathCertificateNumber": "DC-2023-006",
            "Notes": "Multiple bank accounts across different institutions."
        },
        
        # Scenario 7: Insurance policies holder
        {
            "NationalId": "700700700",
            "FirstName": "James",
            "MiddleName": "Robert",
            "LastName": "Davis",
            "Gender": "Male",
            "DateOfBirth": "1960-02-14",
            "DateOfDeath": "2023-07-30",
            "PlaceOfBirth": "Seattle, USA",
            "PlaceOfDeath": "Seattle, USA",
            "Address": "4500 Pike Street, Seattle, WA 98101",
            "Occupation": "Insurance Agent",
            "MaritalStatus": "Married",
            "NextOfKin": "Susan Davis (Spouse)",
            "DeathCertificateNumber": "DC-2023-007",
            "Notes": "Multiple insurance policies including life and health."
        },
        
        # Scenario 8: Investment portfolio
        {
            "NationalId": "800800800",
            "FirstName": "Linda",
            "MiddleName": "Marie",
            "LastName": "Garcia",
            "Gender": "Female",
            "DateOfBirth": "1948-08-03",
            "DateOfDeath": "2023-08-15",
            "PlaceOfBirth": "Houston, USA",
            "PlaceOfDeath": "Houston, USA",
            "Address": "2000 Main Street, Houston, TX 77002",
            "Occupation": "Financial Advisor",
            "MaritalStatus": "Widowed",
            "NextOfKin": "Maria Garcia (Daughter)",
            "DeathCertificateNumber": "DC-2023-008",
            "Notes": "Extensive investment portfolio with multiple accounts."
        },
        
        # Scenario 9: Vehicle owner
        {
            "NationalId": "900900900",
            "FirstName": "Thomas",
            "MiddleName": "Edward",
            "LastName": "Wilson",
            "Gender": "Male",
            "DateOfBirth": "1952-10-20",
            "DateOfDeath": "2023-09-12",
            "PlaceOfBirth": "Phoenix, USA",
            "PlaceOfDeath": "Phoenix, USA",
            "Address": "1500 Central Avenue, Phoenix, AZ 85004",
            "Occupation": "Retired Mechanic",
            "MaritalStatus": "Married",
            "NextOfKin": "Nancy Wilson (Spouse)",
            "DeathCertificateNumber": "DC-2023-009",
            "Notes": "Classic car collection and vehicle assets."
        },
        
        # Scenario 10: Mixed assets
        {
            "NationalId": "101101101",
            "FirstName": "Barbara",
            "MiddleName": "Jean",
            "LastName": "Moore",
            "Gender": "Female",
            "DateOfBirth": "1943-04-17",
            "DateOfDeath": "2023-10-25",
            "PlaceOfBirth": "Denver, USA",
            "PlaceOfDeath": "Denver, USA",
            "Address": "800 Broadway, Denver, CO 80203",
            "Occupation": "Retired Librarian",
            "MaritalStatus": "Single",
            "NextOfKin": "Robert Moore (Brother)",
            "DeathCertificateNumber": "DC-2023-010",
            "Notes": "Mix of bank accounts, investments, and insurance."
        },
    ]
    
    deceased_ids = []
    for dec_data in deceased_data:
        try:
            dec_id = deceased_model.create(dec_data)
            deceased_ids.append(dec_id)
            print(f"  ✅ {dec_data['FirstName']} {dec_data['LastName']} (ID: {dec_id}) - {dec_data.get('Notes', '')[:50]}")
        except Exception as e:
            print(f"  ❌ Error creating {dec_data['FirstName']} {dec_data['LastName']}: {e}")
    
    return deceased_ids

def create_assets(institution_ids, deceased_ids):
    """Create diverse assets showcasing different types and scenarios"""
    print("\n" + "=" * 60)
    print("CREATING ASSETS")
    print("=" * 60)
    
    assets_model = AssetsModel()
    asset_ids = []
    
    # Use stored procedure for asset creation to handle detail tables
    from auth.session import get_current_user
    current_user = get_current_user()
    if not current_user:
        # Set a default user for operations
        set_current_user({"UserId": 1, "Username": "admin", "Role": "Admin"})
    
    # Scenario 1: High-value estate - Multiple assets (Robert Anderson)
    if len(deceased_ids) > 0:
        # Bank Account 1
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[0],
            institution_id=institution_ids[0],  # First National Bank
            asset_type="Bank Account",
            identifier="ACC-ROB-001",
            estimated_value=250000.00,
            account_status="Active",
            account_opening_date="1995-01-15",
            last_transaction_date="2023-01-10",
            interest_rate=2.5,
            account_holder_name="Robert J. Anderson",
            branch_location="Park Avenue Branch",
            currency="USD",
            notes="Primary checking account",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Bank Account: $250,000 (ID: {asset_id}) - Robert Anderson")
        
        # Investment Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[0],
            institution_id=institution_ids[7],  # XYZ Investment Group
            asset_type="Investment",
            identifier="INV-ROB-001",
            estimated_value=500000.00,
            investment_type="Stocks & Bonds",
            account_status="Active",
            account_opening_date="2000-06-20",
            maturity_date=None,
            interest_rate=7.5,
            currency="USD",
            notes="Diversified investment portfolio",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Investment: $500,000 (ID: {asset_id}) - Robert Anderson")
        
        # Life Insurance Policy
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[0],
            institution_id=institution_ids[4],  # ABC Insurance
            asset_type="Insurance Policy",
            identifier="POL-ROB-001",
            estimated_value=1000000.00,
            policy_number="LIFE-2020-5001",
            policy_type="Life Insurance",
            policy_start_date="2020-03-01",
            policy_end_date="2040-03-01",
            premium_amount=5000.00,
            notes="Term life insurance policy",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Insurance: $1,000,000 (ID: {asset_id}) - Robert Anderson")
        
        # Real Estate
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[0],
            institution_id=institution_ids[10],  # Metro Property Management
            asset_type="Real Estate",
            identifier="RE-ROB-001",
            estimated_value=750000.00,
            property_address="1000 Park Avenue, New York, NY 10021",
            property_type="Residential",
            property_size=3500.00,
            property_condition="Excellent",
            property_tax_id="NY-2023-001",
            notes="Primary residence - Luxury apartment",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Real Estate: $750,000 (ID: {asset_id}) - Robert Anderson")
    
    # Scenario 2: Moderate assets (Margaret Thompson)
    if len(deceased_ids) > 1:
        # Bank Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[1],
            institution_id=institution_ids[1],  # Metro Savings Bank
            asset_type="Bank Account",
            identifier="ACC-MAR-001",
            estimated_value=85000.00,
            account_status="Active",
            account_opening_date="1980-05-10",
            last_transaction_date="2023-02-01",
            interest_rate=1.8,
            account_holder_name="Margaret E. Thompson",
            branch_location="Beacon Street Branch",
            currency="USD",
            notes="Savings account from teaching career",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Bank Account: $85,000 (ID: {asset_id}) - Margaret Thompson")
        
        # Pension/Retirement Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[1],
            institution_id=institution_ids[8],  # Global Wealth Management
            asset_type="Investment",
            identifier="INV-MAR-001",
            estimated_value=120000.00,
            investment_type="Retirement Account",
            account_status="Active",
            account_opening_date="1985-09-01",
            interest_rate=5.2,
            currency="USD",
            notes="Teacher pension fund",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Retirement Account: $120,000 (ID: {asset_id}) - Margaret Thompson")
    
    # Scenario 3: Young professional (Michael Chen)
    if len(deceased_ids) > 2:
        # Bank Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[2],
            institution_id=institution_ids[0],  # First National Bank
            asset_type="Bank Account",
            identifier="ACC-MIC-001",
            estimated_value=45000.00,
            account_status="Active",
            account_opening_date="2010-08-15",
            last_transaction_date="2023-03-05",
            interest_rate=0.5,
            account_holder_name="Michael D. Chen",
            branch_location="Market Street Branch",
            currency="USD",
            notes="Tech salary savings",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Bank Account: $45,000 (ID: {asset_id}) - Michael Chen")
        
        # Investment Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[2],
            institution_id=institution_ids[7],  # XYZ Investment Group
            asset_type="Investment",
            identifier="INV-MIC-001",
            estimated_value=75000.00,
            investment_type="Stocks",
            account_status="Active",
            account_opening_date="2015-01-20",
            interest_rate=8.0,
            currency="USD",
            notes="Tech stock portfolio",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Investment: $75,000 (ID: {asset_id}) - Michael Chen")
        
        # Life Insurance
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[2],
            institution_id=institution_ids[4],  # ABC Insurance
            asset_type="Insurance Policy",
            identifier="POL-MIC-001",
            estimated_value=250000.00,
            policy_number="LIFE-2018-3001",
            policy_type="Life Insurance",
            policy_start_date="2018-05-01",
            policy_end_date="2038-05-01",
            premium_amount=1200.00,
            notes="Term life insurance - young professional",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Insurance: $250,000 (ID: {asset_id}) - Michael Chen")
    
    # Scenario 4: Long-term investments (Eleanor Martinez)
    if len(deceased_ids) > 3:
        # Multiple Investment Accounts
        for i, inv_type in enumerate(["Bonds", "Mutual Funds", "Stocks"]):
            success, asset_id, error = db_ops.create_asset_with_validation(
                deceased_id=deceased_ids[3],
                institution_id=institution_ids[8 + (i % 2)],  # Alternate investment firms
                asset_type="Investment",
                identifier=f"INV-ELE-00{i+1}",
                estimated_value=60000.00 + (i * 10000),
                investment_type=inv_type,
                account_status="Active",
                account_opening_date=f"1990-{3+i*3:02d}-15",
                interest_rate=6.0 + i,
                currency="USD",
                notes=f"Long-term {inv_type.lower()} investment",
                user_id=1
            )
            if success:
                asset_ids.append(asset_id)
                print(f"  ✅ Investment ({inv_type}): ${60000 + i*10000} (ID: {asset_id}) - Eleanor Martinez")
    
    # Scenario 5: Real Estate holdings (William Johnson)
    if len(deceased_ids) > 4:
        # Residential Property
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[4],
            institution_id=institution_ids[10],  # Metro Property Management
            asset_type="Real Estate",
            identifier="RE-WIL-001",
            estimated_value=450000.00,
            property_address="1200 Michigan Avenue, Chicago, IL 60611",
            property_type="Residential",
            property_size=2800.00,
            property_condition="Good",
            property_tax_id="IL-2023-001",
            notes="Primary residence",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Real Estate: $450,000 (ID: {asset_id}) - William Johnson")
        
        # Commercial Property
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[4],
            institution_id=institution_ids[11],  # Heritage Realty Group
            asset_type="Real Estate",
            identifier="RE-WIL-002",
            estimated_value=850000.00,
            property_address="500 Commercial Blvd, Chicago, IL 60601",
            property_type="Commercial",
            property_size=5000.00,
            property_condition="Excellent",
            property_tax_id="IL-2023-002",
            notes="Commercial rental property",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Real Estate (Commercial): $850,000 (ID: {asset_id}) - William Johnson")
    
    # Scenario 6: Multiple bank accounts (Patricia Williams)
    if len(deceased_ids) > 5:
        for i, bank_idx in enumerate([0, 1, 2]):  # Different banks
            success, asset_id, error = db_ops.create_asset_with_validation(
                deceased_id=deceased_ids[5],
                institution_id=institution_ids[bank_idx],
                asset_type="Bank Account",
                identifier=f"ACC-PAT-00{i+1}",
                estimated_value=30000.00 + (i * 15000),
                account_status="Active",
                account_opening_date=f"200{i}-{1+i*4:02d}-10",
                last_transaction_date="2023-06-15",
                interest_rate=1.5 + (i * 0.3),
                account_holder_name="Patricia A. Williams",
                branch_location=f"Branch {i+1}",
                currency="USD",
                notes=f"Bank account #{i+1}",
                user_id=1
            )
            if success:
                asset_ids.append(asset_id)
                print(f"  ✅ Bank Account #{i+1}: ${30000 + i*15000} (ID: {asset_id}) - Patricia Williams")
    
    # Scenario 7: Insurance policies (James Davis)
    if len(deceased_ids) > 6:
        # Life Insurance
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[6],
            institution_id=institution_ids[4],  # ABC Insurance
            asset_type="Insurance Policy",
            identifier="POL-JAM-001",
            estimated_value=500000.00,
            policy_number="LIFE-2015-4001",
            policy_type="Life Insurance",
            policy_start_date="2015-07-01",
            policy_end_date="2035-07-01",
            premium_amount=3500.00,
            notes="Term life insurance",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Life Insurance: $500,000 (ID: {asset_id}) - James Davis")
        
        # Health Insurance (as asset)
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[6],
            institution_id=institution_ids[6],  # Premier Health Insurance
            asset_type="Insurance Policy",
            identifier="POL-JAM-002",
            estimated_value=50000.00,
            policy_number="HEALTH-2020-2001",
            policy_type="Health Insurance",
            policy_start_date="2020-01-01",
            policy_end_date="2024-12-31",
            premium_amount=6000.00,
            notes="Health insurance policy",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Health Insurance: $50,000 (ID: {asset_id}) - James Davis")
    
    # Scenario 8: Investment portfolio (Linda Garcia)
    if len(deceased_ids) > 7:
        investment_types = ["Stocks", "Bonds", "Mutual Funds", "ETF"]
        for i, inv_type in enumerate(investment_types):
            success, asset_id, error = db_ops.create_asset_with_validation(
                deceased_id=deceased_ids[7],
                institution_id=institution_ids[7 + (i % 2)],  # Investment firms
                asset_type="Investment",
                identifier=f"INV-LIN-00{i+1}",
                estimated_value=80000.00 + (i * 20000),
                investment_type=inv_type,
                account_status="Active",
                account_opening_date=f"2005-{1+i*3:02d}-10",
                interest_rate=7.0 + (i * 0.5),
                currency="USD",
                notes=f"{inv_type} portfolio",
                user_id=1
            )
            if success:
                asset_ids.append(asset_id)
                print(f"  ✅ Investment ({inv_type}): ${80000 + i*20000} (ID: {asset_id}) - Linda Garcia")
    
    # Scenario 9: Vehicle assets (Thomas Wilson)
    if len(deceased_ids) > 8:
        vehicles = [
            {"make": "Ford", "model": "Mustang", "year": 1967, "value": 45000},
            {"make": "Chevrolet", "model": "Corvette", "year": 1970, "value": 65000},
            {"make": "Porsche", "model": "911", "year": 1985, "value": 85000},
        ]
        
        for i, vehicle in enumerate(vehicles):
            # Note: Vehicle assets need to be created as "Vehicle" type
            # We'll use a generic asset for now since Vehicle detail table needs special handling
            success, asset_id, error = db_ops.create_asset_with_validation(
                deceased_id=deceased_ids[8],
                institution_id=institution_ids[0],  # Using bank as placeholder
                asset_type="Vehicle",
                identifier=f"VEH-THO-00{i+1}",
                estimated_value=float(vehicle["value"]),
                vehicle_make=vehicle["make"],
                vehicle_model=vehicle["model"],
                vehicle_year=vehicle["year"],
                vehicle_vin=f"VIN{vehicle['year']}{i:06d}",
                vehicle_registration=f"REG-{vehicle['year']}-{i+1}",
                vehicle_condition="Excellent",
                vehicle_mileage=50000 - (i * 10000),
                notes=f"{vehicle['year']} {vehicle['make']} {vehicle['model']} - Classic car",
                user_id=1
            )
            if success:
                asset_ids.append(asset_id)
                print(f"  ✅ Vehicle ({vehicle['year']} {vehicle['make']}): ${vehicle['value']} (ID: {asset_id}) - Thomas Wilson")
    
    # Scenario 10: Mixed assets (Barbara Moore)
    if len(deceased_ids) > 9:
        # Bank Account
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[9],
            institution_id=institution_ids[1],  # Metro Savings Bank
            asset_type="Bank Account",
            identifier="ACC-BAR-001",
            estimated_value=55000.00,
            account_status="Active",
            account_opening_date="1975-03-20",
            last_transaction_date="2023-10-20",
            interest_rate=2.0,
            account_holder_name="Barbara J. Moore",
            currency="USD",
            notes="Savings account",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Bank Account: $55,000 (ID: {asset_id}) - Barbara Moore")
        
        # Investment
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[9],
            institution_id=institution_ids[8],  # Global Wealth Management
            asset_type="Investment",
            identifier="INV-BAR-001",
            estimated_value=95000.00,
            investment_type="Mutual Funds",
            account_status="Active",
            account_opening_date="1995-09-15",
            interest_rate=6.5,
            currency="USD",
            notes="Retirement mutual funds",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Investment: $95,000 (ID: {asset_id}) - Barbara Moore")
        
        # Insurance
        success, asset_id, error = db_ops.create_asset_with_validation(
            deceased_id=deceased_ids[9],
            institution_id=institution_ids[5],  # State Life Insurance
            asset_type="Insurance Policy",
            identifier="POL-BAR-001",
            estimated_value=200000.00,
            policy_number="LIFE-2010-6001",
            policy_type="Life Insurance",
            policy_start_date="2010-11-01",
            policy_end_date="2030-11-01",
            premium_amount=2500.00,
            notes="Whole life insurance",
            user_id=1
        )
        if success:
            asset_ids.append(asset_id)
            print(f"  ✅ Insurance: $200,000 (ID: {asset_id}) - Barbara Moore")
    
    return asset_ids

def create_claimants():
    """Create diverse claimants with different relationships"""
    print("\n" + "=" * 60)
    print("CREATING CLAIMANTS")
    print("=" * 60)
    
    claimants_model = ClaimantsModel()
    
    claimants_data = [
        # Spouses
        {"NationalId": "201201201", "FirstName": "Margaret", "LastName": "Anderson", "Relationship": "Spouse", "Contact": "margaret.anderson@email.com", "Email": "margaret.anderson@email.com", "Phone": "555-2001", "Address": "1000 Park Avenue, New York, NY 10021"},
        {"NationalId": "301301301", "FirstName": "Susan", "LastName": "Davis", "Relationship": "Spouse", "Contact": "susan.davis@email.com", "Email": "susan.davis@email.com", "Phone": "555-2007", "Address": "4500 Pike Street, Seattle, WA 98101"},
        {"NationalId": "501501501", "FirstName": "Patricia", "LastName": "Johnson", "Relationship": "Spouse", "Contact": "patricia.johnson@email.com", "Email": "patricia.johnson@email.com", "Phone": "555-2005", "Address": "1200 Michigan Avenue, Chicago, IL 60611"},
        {"NationalId": "901901901", "FirstName": "Nancy", "LastName": "Wilson", "Relationship": "Spouse", "Contact": "nancy.wilson@email.com", "Email": "nancy.wilson@email.com", "Phone": "555-2009", "Address": "1500 Central Avenue, Phoenix, AZ 85004"},
        
        # Children
        {"NationalId": "202202202", "FirstName": "David", "LastName": "Thompson", "Relationship": "Son", "Contact": "david.thompson@email.com", "Email": "david.thompson@email.com", "Phone": "555-2002", "Address": "2500 Beacon Street, Boston, MA 02108"},
        {"NationalId": "302302302", "FirstName": "Lisa", "LastName": "Chen", "Relationship": "Sister", "Contact": "lisa.chen@email.com", "Email": "lisa.chen@email.com", "Phone": "555-2003", "Address": "500 Market Street, San Francisco, CA 94105"},
        {"NationalId": "402402402", "FirstName": "Carlos", "LastName": "Martinez", "Relationship": "Son", "Contact": "carlos.martinez@email.com", "Email": "carlos.martinez@email.com", "Phone": "555-2004", "Address": "7500 Sunset Boulevard, Los Angeles, CA 90046"},
        {"NationalId": "802802802", "FirstName": "Maria", "LastName": "Garcia", "Relationship": "Daughter", "Contact": "maria.garcia@email.com", "Email": "maria.garcia@email.com", "Phone": "555-2008", "Address": "2000 Main Street, Houston, TX 77002"},
        
        # Siblings
        {"NationalId": "101101101", "FirstName": "Robert", "LastName": "Moore", "Relationship": "Brother", "Contact": "robert.moore@email.com", "Email": "robert.moore@email.com", "Phone": "555-2010", "Address": "800 Broadway, Denver, CO 80203"},
        
        # Extended family
        {"NationalId": "203203203", "FirstName": "Jennifer", "LastName": "Anderson", "Relationship": "Daughter", "Contact": "jennifer.anderson@email.com", "Email": "jennifer.anderson@email.com", "Phone": "555-2011", "Address": "1000 Park Avenue, New York, NY 10021"},
        {"NationalId": "204204204", "FirstName": "Robert", "LastName": "Anderson", "Relationship": "Son", "Contact": "robert.anderson.jr@email.com", "Email": "robert.anderson.jr@email.com", "Phone": "555-2012", "Address": "1000 Park Avenue, New York, NY 10021"},
    ]
    
    claimant_ids = []
    for claimant_data in claimants_data:
        try:
            claimant_id = claimants_model.create(claimant_data)
            claimant_ids.append(claimant_id)
            print(f"  ✅ {claimant_data['Relationship']}: {claimant_data['FirstName']} {claimant_data['LastName']} (ID: {claimant_id})")
        except Exception as e:
            if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
                # Try to get existing claimant
                try:
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT ClaimantId FROM Claimants WHERE NationalId = ?", (claimant_data["NationalId"],))
                        row = cursor.fetchone()
                        if row:
                            claimant_ids.append(row[0])
                            print(f"  ⚠️  {claimant_data['FirstName']} {claimant_data['LastName']} already exists (ID: {row[0]})")
                except:
                    pass
            else:
                print(f"  ❌ Error creating {claimant_data['FirstName']} {claimant_data['LastName']}: {e}")
    
    return claimant_ids

def create_claims(asset_ids, claimant_ids):
    """Create claims with different statuses and scenarios"""
    print("\n" + "=" * 60)
    print("CREATING CLAIMS")
    print("=" * 60)
    
    claims_model = ClaimsModel()
    
    # Map assets to claimants based on relationships
    # We'll create various scenarios:
    # - Multiple claims per asset (disputes)
    # - Different claim statuses
    # - Claims at different stages
    
    claims_to_create = []
    
    # Scenario 1: High-value estate - Spouse and children both claiming
    if len(asset_ids) > 0 and len(claimant_ids) > 0:
        # Spouse claims all assets
        claims_to_create.append({
            "AssetId": asset_ids[0],  # Bank account
            "ClaimantId": claimant_ids[0],  # Margaret Anderson (Spouse)
            "Status": "Verified",
            "Notes": "Spouse claim - verified documents"
        })
        claims_to_create.append({
            "AssetId": asset_ids[1],  # Investment
            "ClaimantId": claimant_ids[0],  # Spouse
            "Status": "Settled",
            "Notes": "Investment account - settled to spouse"
        })
        claims_to_create.append({
            "AssetId": asset_ids[2],  # Insurance
            "ClaimantId": claimant_ids[0],  # Spouse
            "Status": "Verified",
            "Notes": "Life insurance - beneficiary verified"
        })
        
        # Children also claiming (dispute scenario)
        if len(claimant_ids) > 9:
            claims_to_create.append({
                "AssetId": asset_ids[1],  # Investment (same asset, different claimant)
                "ClaimantId": claimant_ids[9],  # Jennifer Anderson (Daughter)
                "Status": "Pending",
                "Notes": "Daughter claims partial inheritance - under review"
            })
    
    # Scenario 2: Moderate assets - Son claiming
    if len(asset_ids) > 3 and len(claimant_ids) > 4:
        claims_to_create.append({
            "AssetId": asset_ids[3],  # Bank account
            "ClaimantId": claimant_ids[4],  # David Thompson (Son)
            "Status": "Pending",
            "Notes": "Son claiming mother's savings account - awaiting documents"
        })
        claims_to_create.append({
            "AssetId": asset_ids[4],  # Retirement account
            "ClaimantId": claimant_ids[4],  # Son
            "Status": "Verified",
            "Notes": "Retirement account - verified beneficiary"
        })
    
    # Scenario 3: Young professional - Sister claiming
    if len(asset_ids) > 5 and len(claimant_ids) > 5:
        claims_to_create.append({
            "AssetId": asset_ids[5],  # Bank account
            "ClaimantId": claimant_ids[5],  # Lisa Chen (Sister)
            "Status": "Pending",
            "Notes": "Sister claiming brother's assets - initial submission"
        })
        claims_to_create.append({
            "AssetId": asset_ids[6],  # Investment
            "ClaimantId": claimant_ids[5],  # Sister
            "Status": "Verified",
            "Notes": "Investment account verified"
        })
        claims_to_create.append({
            "AssetId": asset_ids[7],  # Insurance
            "ClaimantId": claimant_ids[5],  # Sister
            "Status": "Settled",
            "Notes": "Life insurance settled to sister"
        })
    
    # Scenario 4: Long-term investments - Son claiming
    if len(asset_ids) > 8 and len(claimant_ids) > 6:
        for i in range(3):  # Multiple investment accounts
            if len(asset_ids) > 8 + i:
                claims_to_create.append({
                    "AssetId": asset_ids[8 + i],
                    "ClaimantId": claimant_ids[6],  # Carlos Martinez (Son)
                    "Status": "Verified" if i < 2 else "Pending",
                    "Notes": f"Investment account #{i+1} - {'verified' if i < 2 else 'under review'}"
                })
    
    # Scenario 5: Real estate - Spouse claiming
    if len(asset_ids) > 11 and len(claimant_ids) > 2:
        claims_to_create.append({
            "AssetId": asset_ids[11],  # Residential property
            "ClaimantId": claimant_ids[2],  # Patricia Johnson (Spouse)
            "Status": "Verified",
            "Notes": "Primary residence - spouse verified"
        })
        claims_to_create.append({
            "AssetId": asset_ids[12],  # Commercial property
            "ClaimantId": claimant_ids[2],  # Spouse
            "Status": "Pending",
            "Notes": "Commercial property - title verification in progress"
        })
    
    # Scenario 6: Multiple bank accounts - Spouse claiming
    if len(asset_ids) > 13 and len(claimant_ids) > 2:
        for i in range(3):
            if len(asset_ids) > 13 + i:
                claims_to_create.append({
                    "AssetId": asset_ids[13 + i],
                    "ClaimantId": claimant_ids[2],  # Patricia Johnson (Spouse)
                    "Status": "Settled" if i == 0 else ("Verified" if i == 1 else "Pending"),
                    "Notes": f"Bank account #{i+1} - {'settled' if i == 0 else ('verified' if i == 1 else 'pending')}"
                })
    
    # Scenario 7: Insurance policies - Spouse claiming
    if len(asset_ids) > 16 and len(claimant_ids) > 1:
        claims_to_create.append({
            "AssetId": asset_ids[16],  # Life insurance
            "ClaimantId": claimant_ids[1],  # Susan Davis (Spouse)
            "Status": "Settled",
            "Notes": "Life insurance policy settled"
        })
        claims_to_create.append({
            "AssetId": asset_ids[17],  # Health insurance
            "ClaimantId": claimant_ids[1],  # Spouse
            "Status": "Rejected",
            "Notes": "Health insurance claim rejected - policy expired"
        })
    
    # Scenario 8: Investment portfolio - Daughter claiming
    if len(asset_ids) > 18 and len(claimant_ids) > 7:
        for i in range(4):
            if len(asset_ids) > 18 + i:
                statuses = ["Settled", "Verified", "Verified", "Pending"]
                claims_to_create.append({
                    "AssetId": asset_ids[18 + i],
                    "ClaimantId": claimant_ids[7],  # Maria Garcia (Daughter)
                    "Status": statuses[i],
                    "Notes": f"Investment account #{i+1} - {statuses[i].lower()}"
                })
    
    # Scenario 9: Vehicles - Spouse claiming
    if len(asset_ids) > 22 and len(claimant_ids) > 3:
        for i in range(3):
            if len(asset_ids) > 22 + i:
                claims_to_create.append({
                    "AssetId": asset_ids[22 + i],
                    "ClaimantId": claimant_ids[3],  # Nancy Wilson (Spouse)
                    "Status": "Verified" if i < 2 else "Pending",
                    "Notes": f"Classic car #{i+1} - {'verified' if i < 2 else 'appraisal pending'}"
                })
    
    # Scenario 10: Mixed assets - Brother claiming
    if len(asset_ids) > 25 and len(claimant_ids) > 8:
        claims_to_create.append({
            "AssetId": asset_ids[25],  # Bank account
            "ClaimantId": claimant_ids[8],  # Robert Moore (Brother)
            "Status": "Pending",
            "Notes": "Brother claiming sister's bank account - awaiting proof of relationship"
        })
        claims_to_create.append({
            "AssetId": asset_ids[26],  # Investment
            "ClaimantId": claimant_ids[8],  # Brother
            "Status": "Verified",
            "Notes": "Investment account verified to brother"
        })
        claims_to_create.append({
            "AssetId": asset_ids[27],  # Insurance
            "ClaimantId": claimant_ids[8],  # Brother
            "Status": "Pending",
            "Notes": "Insurance claim - beneficiary verification in progress"
        })
    
    # Create all claims
    created_claims = []
    for claim_data in claims_to_create:
        try:
            claim_id = claims_model.create(claim_data, use_stored_procedure=True)
            created_claims.append(claim_id)
            print(f"  ✅ Claim (ID: {claim_id}) - Status: {claim_data['Status']} - Asset: {claim_data['AssetId']}, Claimant: {claim_data['ClaimantId']}")
        except Exception as e:
            print(f"  ❌ Error creating claim: {e}")
    
    return created_claims

def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE DATABASE SEEDING")
    print("=" * 60)
    print("\nThis will populate the database with extensive sample data")
    print("showcasing various scenarios and use cases.\n")
    
    try:
        # Step 1: Create users
        users = create_users()
        
        # Step 2: Create institutions
        institution_ids = create_institutions()
        
        # Step 3: Create deceased records
        deceased_ids = create_deceased_records()
        
        # Step 4: Create assets
        asset_ids = create_assets(institution_ids, deceased_ids)
        
        # Step 5: Create claimants
        claimant_ids = create_claimants()
        
        # Step 6: Create claims
        claim_ids = create_claims(asset_ids, claimant_ids)
        
        # Summary
        print("\n" + "=" * 60)
        print("SEEDING SUMMARY")
        print("=" * 60)
        print(f"✅ Users created: {len(users)}")
        print(f"✅ Institutions created: {len(institution_ids)}")
        print(f"✅ Deceased records created: {len(deceased_ids)}")
        print(f"✅ Assets created: {len(asset_ids)}")
        print(f"✅ Claimants created: {len(claimant_ids)}")
        print(f"✅ Claims created: {len(claim_ids)}")
        
        print("\n" + "=" * 60)
        print("LOGIN CREDENTIALS")
        print("=" * 60)
        print("Admin: admin / admin123")
        print("Staff: staff1 / staff123")
        print("Staff: staff2 / staff123")
        print("Viewer: viewer1 / viewer123")
        
        print("\n" + "=" * 60)
        print("SCENARIOS CREATED")
        print("=" * 60)
        print("1. High-value estate (multiple assets, $1.5M+)")
        print("2. Moderate assets (retirement accounts)")
        print("3. Young professional (tech investments)")
        print("4. Long-term investments (diversified portfolio)")
        print("5. Real estate holdings (residential + commercial)")
        print("6. Multiple bank accounts (across institutions)")
        print("7. Insurance policies (life + health)")
        print("8. Investment portfolio (stocks, bonds, funds)")
        print("9. Vehicle assets (classic car collection)")
        print("10. Mixed assets (bank + investment + insurance)")
        
        print("\n🎉 Database seeding completed successfully!")
        print("   You can now login and explore all the scenarios!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()

