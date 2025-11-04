"""
Case management model stubs: Cases, Tasks, Notes, Attachments, StatusHistory.

These provide minimal CRUD-like methods to support workflow and tracking.
"""

from typing import Optional, Dict, Any, List

from db.db_connect import get_connection


class CasesModel:
    def create(self, *, title: str, description: Optional[str] = None, deceased_id: Optional[int] = None, claim_id: Optional[int] = None, created_by_user_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO Cases (DeceasedId, ClaimId, Title, Description, CreatedByUserId) OUTPUT INSERTED.CaseId VALUES (?, ?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (deceased_id, claim_id, title, description, created_by_user_id))
            row = cur.fetchone()
            return int(row[0])

    def update_status(self, case_id: int, status: str) -> bool:
        query = "UPDATE Cases SET Status = CASE WHEN Status <> ? THEN ? ELSE Status END WHERE CaseId = ?"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (status, status, case_id))
            return cur.rowcount > 0

    def list(self) -> List[Dict[str, Any]]:
        query = "SELECT CaseId, DeceasedId, ClaimId, Title, Status, OpenedAt, ClosedAt FROM Cases ORDER BY OpenedAt DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            return [
                {
                    "CaseId": r[0],
                    "DeceasedId": r[1],
                    "ClaimId": r[2],
                    "Title": r[3],
                    "Status": r[4],
                    "OpenedAt": r[5],
                    "ClosedAt": r[6],
                }
                for r in rows
            ]


class TasksModel:
    def add(self, *, case_id: int, title: str, status: str = "Pending", due_date: Optional[str] = None, assigned_to_user_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO Tasks (CaseId, Title, Status, DueDate, AssignedToUserId) OUTPUT INSERTED.TaskId VALUES (?, ?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (case_id, title, status, due_date, assigned_to_user_id))
            row = cur.fetchone()
            return int(row[0])

    def list_for_case(self, case_id: int) -> List[Dict[str, Any]]:
        query = "SELECT TaskId, Title, Status, DueDate, CreatedAt, AssignedToUserId FROM Tasks WHERE CaseId = ? ORDER BY CreatedAt DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (case_id,))
            rows = cur.fetchall()
            return [
                {
                    "TaskId": r[0],
                    "Title": r[1],
                    "Status": r[2],
                    "DueDate": r[3],
                    "CreatedAt": r[4],
                    "AssignedToUserId": r[5],
                }
                for r in rows
            ]


class NotesModel:
    def add(self, *, case_id: int, content: str, user_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO Notes (CaseId, UserId, Content) OUTPUT INSERTED.NoteId VALUES (?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (case_id, user_id, content))
            row = cur.fetchone()
            return int(row[0])

    def list_for_case(self, case_id: int) -> List[Dict[str, Any]]:
        query = "SELECT NoteId, UserId, Content, CreatedAt FROM Notes WHERE CaseId = ? ORDER BY CreatedAt DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (case_id,))
            rows = cur.fetchall()
            return [
                {"NoteId": r[0], "UserId": r[1], "Content": r[2], "CreatedAt": r[3]} for r in rows
            ]


class AttachmentsModel:
    def add(self, *, entity_type: str, entity_id: int, file_name: str, location: str, mime_type: Optional[str] = None, uploaded_by_user_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO Attachments (EntityType, EntityId, FileName, MimeType, Location, UploadedByUserId) OUTPUT INSERTED.AttachmentId VALUES (?, ?, ?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (entity_type, entity_id, file_name, mime_type, location, uploaded_by_user_id))
            row = cur.fetchone()
            return int(row[0])

    def list_for(self, *, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        query = "SELECT AttachmentId, FileName, MimeType, Location, UploadedAt, UploadedByUserId FROM Attachments WHERE EntityType = ? AND EntityId = ? ORDER BY UploadedAt DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (entity_type, entity_id))
            rows = cur.fetchall()
            return [
                {
                    "AttachmentId": r[0],
                    "FileName": r[1],
                    "MimeType": r[2],
                    "Location": r[3],
                    "UploadedAt": r[4],
                    "UploadedByUserId": r[5],
                }
                for r in rows
            ]


class StatusHistoryModel:
    def add(self, *, entity_type: str, entity_id: int, status: str, notes: Optional[str] = None, changed_by_user_id: Optional[int] = None) -> int:
        query = (
            "INSERT INTO StatusHistory (EntityType, EntityId, Status, Notes, ChangedByUserId) OUTPUT INSERTED.StatusHistoryId VALUES (?, ?, ?, ?, ?)"
        )
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (entity_type, entity_id, status, notes, changed_by_user_id))
            row = cur.fetchone()
            return int(row[0])

    def list_for(self, *, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        query = "SELECT StatusHistoryId, Status, ChangedAt, ChangedByUserId, Notes FROM StatusHistory WHERE EntityType = ? AND EntityId = ? ORDER BY ChangedAt DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (entity_type, entity_id))
            rows = cur.fetchall()
            return [
                {
                    "StatusHistoryId": r[0],
                    "Status": r[1],
                    "ChangedAt": r[2],
                    "ChangedByUserId": r[3],
                    "Notes": r[4],
                }
                for r in rows
            ]


