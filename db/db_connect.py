"""
Database Connection Module for FARVS

This module provides database connection utilities for SQL Server.
It handles connection creation and connection testing.

Functions:
    get_connection: Create and return a new database connection
    try_connect: Test database connectivity and return status
"""

import pyodbc
from typing import Optional

from config import build_connection_string


def get_connection() -> pyodbc.Connection:
    """
    Create and return a new database connection to SQL Server.
    
    Uses the connection string built from environment variables
    to establish a connection to the FARVS database.
    
    Returns:
        pyodbc.Connection: Active database connection object
    
    Raises:
        pyodbc.Error: If connection fails (server not available, 
                      invalid credentials, etc.)
    
    Example:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Deceased")
        rows = cursor.fetchall()
        conn.close()
    """
    # Build connection string from environment variables
    conn_str = build_connection_string()
    
    # Create and return connection
    return pyodbc.connect(conn_str)


def try_connect() -> tuple[bool, Optional[str]]:
    """
    Test database connectivity without raising exceptions.
    
    Attempts to establish a connection to the database and returns
    a status tuple indicating success or failure with error message.
    
    Returns:
        tuple[bool, Optional[str]]: 
            - First element: True if connection successful, False otherwise
            - Second element: Error message string if failed, None if successful
    
    Example:
        success, error = try_connect()
        if success:
            print("Database connection successful!")
        else:
            print(f"Connection failed: {error}")
    """
    try:
        # Attempt to create connection (using context manager for auto-close)
        with get_connection() as _:
            # Connection successful
            return True, None
    except Exception as exc:  # noqa: BLE001 - surfacing raw error for setup
        # Connection failed - return error message
        return False, str(exc)


