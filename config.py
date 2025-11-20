"""
Configuration Management Module for FARVS

This module handles environment variable loading and database connection string
construction. It uses python-dotenv to load configuration from a .env file.

Functions:
    get_env: Retrieve environment variable with optional default value
    build_connection_string: Construct SQL Server connection string from environment variables
"""

import os
from dotenv import load_dotenv


# Load environment variables from .env file if it exists
load_dotenv()


def get_env(key: str, default: str | None = None) -> str | None:
    """
    Get environment variable value with optional default.
    
    Args:
        key: The environment variable name to retrieve
        default: Optional default value if key is not found
    
    Returns:
        The environment variable value or default if not found
    """
    return os.getenv(key, default)


def build_connection_string() -> str:
    """
    Build SQL Server connection string from environment variables.
    
    Reads database configuration from environment variables and constructs
    a proper ODBC connection string for SQL Server.
    
    Environment Variables Used:
        DB_DRIVER: ODBC driver name (default: "ODBC Driver 17 for SQL Server")
        DB_SERVER: SQL Server instance (default: "localhost\\SQLEXPRESS")
        DB_NAME: Database name (default: "FARVS")
        DB_TRUSTED_CONNECTION: Use Windows authentication (default: "yes")
        DB_USERNAME: SQL Server username (optional)
        DB_PASSWORD: SQL Server password (optional)
        DB_ENCRYPT: Enable encryption (default: "yes")
        DB_TRUST_SERVER_CERTIFICATE: Trust server certificate (default: "yes")
    
    Returns:
        Complete ODBC connection string for SQL Server
    
    Example:
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=FARVS;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;"
    """
    # Get database driver (ODBC driver name)
    driver = get_env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Get server instance name
    server = get_env("DB_SERVER", "localhost\\SQLEXPRESS")
    
    # Get database name
    database = get_env("DB_NAME", "FARVS")
    
    # Check if using Windows authentication (Trusted Connection)
    trusted = (get_env("DB_TRUSTED_CONNECTION", "yes") or "").lower()
    
    # Get SQL Server authentication credentials (if not using Windows auth)
    username = get_env("DB_USERNAME")
    password = get_env("DB_PASSWORD")
    
    # Get encryption settings
    encrypt = get_env("DB_ENCRYPT", "yes").lower()
    trust_cert = get_env("DB_TRUST_SERVER_CERTIFICATE", "yes").lower()

    # Build base connection string components
    conn_parts = [
        f"DRIVER={{{driver}}}",  # Driver name must be in curly braces
        f"SERVER={server}",
        f"DATABASE={database}"
    ]
    
    # Add authentication method
    # Use Windows authentication if trusted connection is enabled or no credentials provided
    if trusted == "yes" or (not username and not password):
        conn_parts.append("Trusted_Connection=yes")
    else:
        # Use SQL Server authentication with username and password
        conn_parts.extend([f"UID={username}", f"PWD={password}"])
    
    # Add encryption settings for secure connections
    if encrypt == "yes":
        conn_parts.append("Encrypt=yes")
        # Trust server certificate (useful for local development)
        if trust_cert == "yes":
            conn_parts.append("TrustServerCertificate=yes")
    
    # Join all parts with semicolons and return complete connection string
    return ";".join(conn_parts) + ";"


