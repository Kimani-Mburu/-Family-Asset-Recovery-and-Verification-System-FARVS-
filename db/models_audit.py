"""
Audit log model stub.

Records who did what and when. Intended to be called from UI or service layer
around CRUD operations (e.g., after creating a claim, record an audit event).
"""

from typing import Optional

from db.db_connect import get_connection


class AuditLogModel:
    def write(self, *, user_id: Optional[int], action: str, entity: str, entity_id: Optional[str], details: Optional[str], ip: Optional[str]) -> None:
        query = (
            "INSERT INTO AuditLog (UserId, Action, Entity, EntityId, Details, IpAddress) VALUES (?, ?, ?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (user_id, action, entity, entity_id, details, ip))


