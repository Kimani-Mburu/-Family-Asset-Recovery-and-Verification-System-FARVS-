"""
Audit Log Model for FARVS

This module provides database operations for audit logging. It records
who performed what action on which entity and when. This is essential
for tracking all changes in the system for security and compliance.

The audit log is automatically populated by triggers for most operations,
but can also be manually called from UI or service layer for custom events.

Classes:
    AuditLogModel: Main class for audit log operations
"""

from typing import Optional

from db.db_connect import get_connection


class AuditLogModel:
    """
    Database model for managing audit log entries.
    
    Provides operations for recording system events:
    - Write: Create audit log entries for tracking changes
    """
    
    def write(self, *, user_id: Optional[int], action: str, entity: str, 
              entity_id: Optional[str], details: Optional[str], 
              ip: Optional[str]) -> None:
        """
        Write an audit log entry.
        
        Records who performed what action on which entity. This method is
        typically called after CRUD operations to maintain an audit trail.
        
        Args:
            user_id: ID of the user who performed the action (None if system action)
            action: Type of action (e.g., 'CREATE', 'UPDATE', 'DELETE', 'ACCESS')
            entity: Entity type (e.g., 'Deceased', 'Asset', 'Claim')
            entity_id: ID of the affected entity (as string for flexibility)
            details: Additional details about the action
            ip: IP address of the user (optional, for security tracking)
        
        Raises:
            pyodbc.Error: If database operation fails
        
        Example:
            # Log a claim creation
            audit.write(
                user_id=1,
                action='CREATE',
                entity='Claim',
                entity_id='123',
                details='Created claim for asset 45',
                ip='192.168.1.1'
            )
        
        Note:
            Most audit logging is handled automatically by triggers.
            This method is for manual logging when needed.
        """
        # SQL query to insert audit log entry
        query = (
            "INSERT INTO AuditLog (UserId, Action, Entity, EntityId, Details, IpAddress) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        
        with get_connection() as conn:
            cur = conn.cursor()
            # Execute query with all audit information
            cur.execute(query, (user_id, action, entity, entity_id, details, ip))
            # Commit is handled by context manager


