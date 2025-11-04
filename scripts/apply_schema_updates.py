"""
Apply FARVS schema updates (handles GO batching).

This script reads `db/farvs_db.sql`, splits statements on GO boundaries,
and executes them against the configured SQL Server using environment-based
connection settings via `config.build_connection_string`.

Usage:
  python scripts/apply_schema_updates.py
"""

import sys
import pyodbc
from pathlib import Path

from config import build_connection_string


def execute_sql_batches(sql_text: str) -> None:
    # Split by GO (standalone on a line) - handle common cases
    batches = []
    current = []
    for line in sql_text.splitlines():
        if line.strip().upper() == "GO":
            if current:
                batches.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        batches.append("\n".join(current).strip())

    conn = pyodbc.connect(build_connection_string(), autocommit=True)
    cur = conn.cursor()
    for idx, batch in enumerate(batches, start=1):
        if not batch:
            continue
        try:
            cur.execute(batch)
            # Avoid verbose output; show short preview
            first = batch.splitlines()[0][:120]
            print(f"OK[{idx}]: {first}")
        except Exception as exc:
            first = batch.splitlines()[0][:120]
            print(f"ERR[{idx}]: {first}\n  {exc}")
    conn.close()


def main() -> int:
    sql_path = Path("db/farvs_db.sql")
    if not sql_path.exists():
        print("Schema file not found: db/farvs_db.sql")
        return 1
    sql_text = sql_path.read_text(encoding="utf-8")
    execute_sql_batches(sql_text)
    print("Schema updates applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


