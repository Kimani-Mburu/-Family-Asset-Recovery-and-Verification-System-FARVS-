"""
Database Seed Script for FARVS

This script populates the database with sample data for testing purposes.
Run this script after creating the database schema to have test data available.

Usage:
    python db/seed_data.py
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_connect import get_connection
from db.models_deceased import DeceasedModel
from db.models_institutions import InstitutionsModel
from db.models_assets import AssetsModel
from db.models_claimants import ClaimantsModel
from db.models_claims import ClaimsModel
from db.models_users import UsersModel
from auth.password import hash_password


def seed_database():
    """Seed the database with sample data."""
    print("Starting database seeding...")
    
    try:
        # Initialize models
        deceased_model = DeceasedModel()
        institutions_model = InstitutionsModel()
        assets_model = AssetsModel()
        claimants_model = ClaimantsModel()
        claims_model = ClaimsModel()
        users_model = UsersModel()
        
        # Check if data already exists
        existing_count = deceased_model.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} deceased records.")
            print("Proceeding with re-seeding (adding sample data if users don't exist)...")
        
        print("Creating sample users...")
        # Create sample users with secure password hashing
        try:
            admin_password_hash = hash_password("admin123")
            admin_id = users_model.create("admin", admin_password_hash, "Admin")
            print(f"  ✓ Created admin user (ID: {admin_id}) - Password: admin123")
        except Exception:
            print("  - Admin user already exists")
        
        try:
            staff_password_hash = hash_password("staff123")
            staff_id = users_model.create("staff", staff_password_hash, "Staff")
            print(f"  ✓ Created staff user (ID: {staff_id}) - Password: staff123")
        except Exception:
            print("  - Staff user already exists")
        
        print("Creating sample institutions...")
        # Create institutions
        institutions_data = [
            {"Name": "First National Bank", "Type": "Bank", "Contact": "contact@fnb.com"},
            {"Name": "ABC Insurance Company", "Type": "Insurance", "Contact": "info@abcinsurance.com"},
            {"Name": "XYZ Investment Group", "Type": "Investment", "Contact": "support@xyzinvest.com"},
            {"Name": "Metro Savings Bank", "Type": "Bank", "Contact": "help@metrosavings.com"},
        ]
        
        institution_ids = []
        for inst_data in institutions_data:
            inst_id = institutions_model.create(inst_data)
            institution_ids.append(inst_id)
            print(f"  ✓ Created institution: {inst_data['Name']} (ID: {inst_id})")
        
        print("Creating sample deceased records...")
        # Create deceased records
        deceased_data = [
            {
                "NationalId": "123456789",
                "FirstName": "John",
                "LastName": "Smith",
                "DateOfBirth": "1950-05-15",
                "DateOfDeath": "2023-03-20"
            },
            {
                "NationalId": "987654321",
                "FirstName": "Mary",
                "LastName": "Johnson",
                "DateOfBirth": "1945-08-22",
                "DateOfDeath": "2023-06-10"
            },
            {
                "NationalId": "456789123",
                "FirstName": "Robert",
                "LastName": "Williams",
                "DateOfBirth": "1960-12-05",
                "DateOfDeath": "2023-09-15"
            },
            {
                "NationalId": "789123456",
                "FirstName": "Sarah",
                "LastName": "Brown",
                "DateOfBirth": "1955-02-28",
                "DateOfDeath": "2023-11-30"
            },
        ]
        
        deceased_ids = []
        for dec_data in deceased_data:
            dec_id = deceased_model.create(dec_data)
            deceased_ids.append(dec_id)
            print(f"  ✓ Created deceased: {dec_data['FirstName']} {dec_data['LastName']} (ID: {dec_id})")
        
        print("Creating sample assets...")
        # Create assets
        assets_data = [
            {
                "DeceasedId": deceased_ids[0],
                "InstitutionId": institution_ids[0],
                "AssetType": "Bank Account",
                "Identifier": "ACC-001-12345",
                "EstimatedValue": 50000.00
            },
            {
                "DeceasedId": deceased_ids[0],
                "InstitutionId": institution_ids[1],
                "AssetType": "Insurance Policy",
                "Identifier": "POL-2023-001",
                "EstimatedValue": 100000.00
            },
            {
                "DeceasedId": deceased_ids[1],
                "InstitutionId": institution_ids[0],
                "AssetType": "Bank Account",
                "Identifier": "ACC-002-67890",
                "EstimatedValue": 25000.00
            },
            {
                "DeceasedId": deceased_ids[1],
                "InstitutionId": institution_ids[2],
                "AssetType": "Investment",
                "Identifier": "INV-2023-045",
                "EstimatedValue": 75000.00
            },
            {
                "DeceasedId": deceased_ids[2],
                "InstitutionId": institution_ids[3],
                "AssetType": "Bank Account",
                "Identifier": "ACC-003-11111",
                "EstimatedValue": 30000.00
            },
            {
                "DeceasedId": deceased_ids[3],
                "InstitutionId": institution_ids[1],
                "AssetType": "Insurance Policy",
                "Identifier": "POL-2023-002",
                "EstimatedValue": 150000.00
            },
        ]
        
        asset_ids = []
        for asset_data in assets_data:
            asset_id = assets_model.create(asset_data)
            asset_ids.append(asset_id)
            print(f"  ✓ Created asset: {asset_data['AssetType']} (ID: {asset_id})")
        
        print("Creating sample claimants...")
        # Create claimants
        claimants_data = [
            {
                "NationalId": "111222333",
                "FirstName": "James",
                "LastName": "Smith",
                "Relationship": "Child",
                "Contact": "james.smith@email.com"
            },
            {
                "NationalId": "444555666",
                "FirstName": "Emily",
                "LastName": "Johnson",
                "Relationship": "Spouse",
                "Contact": "emily.j@email.com"
            },
            {
                "NationalId": "777888999",
                "FirstName": "Michael",
                "LastName": "Williams",
                "Relationship": "Sibling",
                "Contact": "m.williams@email.com"
            },
            {
                "NationalId": "000111222",
                "FirstName": "Lisa",
                "LastName": "Brown",
                "Relationship": "Child",
                "Contact": "lisa.brown@email.com"
            },
        ]
        
        claimant_ids = []
        for claimant_data in claimants_data:
            claimant_id = claimants_model.create(claimant_data)
            claimant_ids.append(claimant_id)
            print(f"  ✓ Created claimant: {claimant_data['FirstName']} {claimant_data['LastName']} (ID: {claimant_id})")
        
        print("Creating sample claims...")
        # Create claims with different statuses
        claims_data = [
            {
                "AssetId": asset_ids[0],
                "ClaimantId": claimant_ids[0],
                "Status": "Pending",
                "Notes": "Initial claim submission"
            },
            {
                "AssetId": asset_ids[1],
                "ClaimantId": claimant_ids[0],
                "Status": "Verified",
                "Notes": "Documents verified, awaiting settlement"
            },
            {
                "AssetId": asset_ids[2],
                "ClaimantId": claimant_ids[1],
                "Status": "Pending",
                "Notes": "Claim submitted, under review"
            },
            {
                "AssetId": asset_ids[3],
                "ClaimantId": claimant_ids[1],
                "Status": "Settled",
                "Notes": "Claim settled and payment processed"
            },
            {
                "AssetId": asset_ids[4],
                "ClaimantId": claimant_ids[2],
                "Status": "Verified",
                "Notes": "Verification complete"
            },
            {
                "AssetId": asset_ids[5],
                "ClaimantId": claimant_ids[3],
                "Status": "Pending",
                "Notes": "New claim, pending verification"
            },
        ]
        
        for claim_data in claims_data:
            claim_id = claims_model.create(claim_data, use_stored_procedure=True)
            print(f"  ✓ Created claim (ID: {claim_id}) - Status: {claim_data['Status']}")
        
        print("\n✓ Database seeding completed successfully!")
        print(f"  - {len(deceased_data)} deceased records")
        print(f"  - {len(institutions_data)} institutions")
        print(f"  - {len(assets_data)} assets")
        print(f"  - {len(claimants_data)} claimants")
        print(f"  - {len(claims_data)} claims")
        print("\nYou can now log in with:")
        print("  Username: admin, Password: admin123")
        print("  Username: staff, Password: staff123")
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    seed_database()

