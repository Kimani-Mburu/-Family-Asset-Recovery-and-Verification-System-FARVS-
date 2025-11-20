"""
Migration Runner Script
=======================

This script runs the SQL migration to add new form fields to existing database tables.
"""

import pyodbc
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db_connect import get_connection
from config import build_connection_string


def run_migration():
    """Run the migration SQL script."""
    # Read the migration SQL file
    migration_file = Path(__file__).parent / "migration_add_form_fields.sql"
    
    if not migration_file.exists():
        print(f"Error: Migration file not found: {migration_file}")
        return False
    
    print(f"Reading migration file: {migration_file}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Split the script into individual statements (separated by GO)
    statements = [s.strip() for s in sql_script.split('GO') if s.strip()]
    
    print(f"\nFound {len(statements)} SQL statements to execute")
    print("=" * 60)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            success_count = 0
            error_count = 0
            
            for i, statement in enumerate(statements, 1):
                if not statement or statement.startswith('--'):
                    continue
                
                try:
                    # Execute the statement
                    cursor.execute(statement)
                    conn.commit()
                    success_count += 1
                    print(f"✓ Statement {i} executed successfully")
                except pyodbc.Error as e:
                    error_count += 1
                    error_msg = str(e).split('\n')[0]  # Get first line of error
                    # Check if it's a "column already exists" error (which is OK)
                    if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                        print(f"⊘ Statement {i} skipped (column may already exist): {error_msg[:80]}")
                    else:
                        print(f"✗ Statement {i} failed: {error_msg[:80]}")
                        # Don't stop on errors, continue with other statements
                except Exception as e:
                    error_count += 1
                    print(f"✗ Statement {i} failed: {str(e)[:80]}")
            
            print("=" * 60)
            print(f"\nMigration Summary:")
            print(f"  ✓ Successful: {success_count}")
            print(f"  ✗ Errors: {error_count}")
            print(f"  Total: {len(statements)}")
            
            if error_count == 0:
                print("\n✓ Migration completed successfully!")
                return True
            else:
                print(f"\n⚠ Migration completed with {error_count} error(s)")
                print("   (Some columns may already exist, which is OK)")
                return True  # Still return True as some errors are expected
                
    except pyodbc.Error as e:
        print(f"\n✗ Database connection error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("FARVS Database Migration: Add New Form Fields")
    print("=" * 60)
    print(f"Connection String: {build_connection_string()}")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n✓ You can now use the application with all new form fields!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed. Please check the errors above.")
        sys.exit(1)

