"""
Asset valuations time-series model stub.

Enables recording historical valuations for assets.
"""

from datetime import date
from typing import List, Dict, Any

from db.db_connect import get_connection


class AssetValuationsModel:
    def add(self, asset_id: int, valuation_date: date, amount: float, source: str | None = None) -> int:
        query = (
            "INSERT INTO AssetValuations (AssetId, ValuationDate, Amount, Source) OUTPUT INSERTED.ValuationId VALUES (?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (asset_id, valuation_date, amount, source))
            row = cur.fetchone()
            return int(row[0])

    def list_for_asset(self, asset_id: int) -> List[Dict[str, Any]]:
        query = (
            "SELECT ValuationId, AssetId, ValuationDate, Amount, Source, CreatedAt FROM AssetValuations WHERE AssetId = ? ORDER BY ValuationDate DESC"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (asset_id,))
            rows = cur.fetchall()
            return [
                {
                    "ValuationId": r[0],
                    "AssetId": r[1],
                    "ValuationDate": r[2],
                    "Amount": r[3],
                    "Source": r[4],
                    "CreatedAt": r[5],
                }
                for r in rows
            ]


