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

    if trusted == "yes" or (not username and not password):
        return (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        )

    return (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    )


