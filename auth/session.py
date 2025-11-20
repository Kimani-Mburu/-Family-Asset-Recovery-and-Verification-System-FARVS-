"""
Session Management Module for FARVS

This module provides in-memory session management for the Tkinter application.
It stores the currently authenticated user information for audit logging
and role-based access control.

The session is stored in memory and persists for the lifetime of the application.
On application restart, users must log in again.

Functions:
    set_current_user: Store the current authenticated user
    get_current_user: Retrieve the current authenticated user
"""

from typing import Optional, Dict, Any

# Global variable to store current user session
# Format: {"UserId": int, "Username": str, "Role": str}
_current_user: Optional[Dict[str, Any]] = None


def set_current_user(user: Optional[Dict[str, Any]]) -> None:
    """
    Set the current authenticated user in the session.
    
    Args:
        user: Dictionary containing user information with keys:
            - UserId: Integer user ID
            - Username: String username
            - Role: String role (e.g., "Admin", "Staff", "Viewer")
            If None, clears the current user session.
    
    Example:
        set_current_user({"UserId": 1, "Username": "admin", "Role": "Admin"})
        set_current_user(None)  # Clear session
    """
    global _current_user
    _current_user = user


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from the session.
    
    Returns:
        Dictionary containing user information if logged in, None otherwise.
        Format: {"UserId": int, "Username": str, "Role": str}
    
    Example:
        user = get_current_user()
        if user:
            print(f"Logged in as: {user['Username']} ({user['Role']})")
        else:
            print("No user logged in")
    """
    return _current_user


