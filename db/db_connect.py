import pyodbc
from typing import Optional

from config import build_connection_string


def get_connection() -> pyodbc.Connection:
    conn_str = build_connection_string()
    return pyodbc.connect(conn_str)


def try_connect() -> tuple[bool, Optional[str]]:
    try:
        with get_connection() as _:
            return True, None
    except Exception as exc:  # noqa: BLE001 - surfacing raw error for setup
        return False, str(exc)


