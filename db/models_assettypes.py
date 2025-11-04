"""
Asset types taxonomy model stub.

Supports listing and simple creation of asset categories with optional parent
for hierarchical organization.
"""

from typing import List, Dict, Any, Optional

from db.db_connect import get_connection


class AssetTypesModel:
    def list(self) -> List[Dict[str, Any]]:
        query = "SELECT AssetTypeId, Name, ParentAssetTypeId FROM AssetTypes ORDER BY Name"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            return [
                {"AssetTypeId": r[0], "Name": r[1], "ParentAssetTypeId": r[2]} for r in rows
            ]

    def create(self, name: str, parent_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO AssetTypes (Name, ParentAssetTypeId) OUTPUT INSERTED.AssetTypeId VALUES (?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (name, parent_id))
            row = cur.fetchone()
            return int(row[0])


