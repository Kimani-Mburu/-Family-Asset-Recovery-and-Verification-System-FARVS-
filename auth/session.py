"""
In-memory session utilities for the running Tkinter app.

Stores the currently authenticated user for AuditLog attribution and
role-based UI decisions.
"""

from typing import Optional, Dict, Any

_current_user: Optional[Dict[str, Any]] = None


def set_current_user(user: Optional[Dict[str, Any]]) -> None:
    global _current_user
    _current_user = user


def get_current_user() -> Optional[Dict[str, Any]]:
    return _current_user


