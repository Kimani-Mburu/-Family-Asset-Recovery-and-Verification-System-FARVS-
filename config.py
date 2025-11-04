import os
from dotenv import load_dotenv


load_dotenv()


def get_env(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)


def build_connection_string() -> str:
    driver = get_env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    server = get_env("DB_SERVER", "localhost\\SQLEXPRESS")
    database = get_env("DB_NAME", "FARVS")
    trusted = (get_env("DB_TRUSTED_CONNECTION", "yes") or "").lower()
    username = get_env("DB_USERNAME")
    password = get_env("DB_PASSWORD")
    encrypt = get_env("DB_ENCRYPT", "yes").lower()
    trust_cert = get_env("DB_TRUST_SERVER_CERTIFICATE", "yes").lower()

    # Build base connection string
    conn_parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}"
    ]
    
    # Add authentication
    if trusted == "yes" or (not username and not password):
        conn_parts.append("Trusted_Connection=yes")
    else:
        conn_parts.extend([f"UID={username}", f"PWD={password}"])
    
    # Add encryption settings
    if encrypt == "yes":
        conn_parts.append("Encrypt=yes")
        if trust_cert == "yes":
            conn_parts.append("TrustServerCertificate=yes")
    
    return ";".join(conn_parts) + ";"


