"""
Password Hashing Module for FARVS

This module provides secure password hashing and verification functions.
Uses SHA-256 with salt for password hashing (production should use bcrypt or PBKDF2).

Functions:
    hash_password: Hash a password with salt
    verify_password: Verify a password against a stored hash
"""

import hashlib
import secrets
from typing import Tuple


def hash_password(password: str) -> bytes:
    """
    Hash a password using SHA-256 with a random salt.
    
    Format: salt (32 bytes) + hash (32 bytes) = 64 bytes total
    The salt is prepended to the hash for storage.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        bytes: Combined salt + hash (64 bytes total)
    
    Example:
        password_hash = hash_password("mypassword123")
        # Store password_hash in database
    """
    # Generate a random 32-byte salt
    salt = secrets.token_bytes(32)
    
    # Hash password with salt using SHA-256
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password_bytes)
    password_hash = hash_obj.digest()
    
    # Return salt + hash (64 bytes total)
    return salt + password_hash


def verify_password(password: str, stored_hash: bytes) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: Plain text password to verify
        stored_hash: Stored hash from database (64 bytes: salt + hash)
    
    Returns:
        bool: True if password matches, False otherwise
    
    Example:
        if verify_password("mypassword123", user["PasswordHash"]):
            print("Password correct")
    """
    if not stored_hash or len(stored_hash) != 64:
        # Invalid hash format (should be 64 bytes: 32 salt + 32 hash)
        return False
    
    # Extract salt (first 32 bytes) and stored hash (last 32 bytes)
    salt = stored_hash[:32]
    stored_password_hash = stored_hash[32:]
    
    # Hash the provided password with the extracted salt
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password_bytes)
    computed_hash = hash_obj.digest()
    
    # Compare hashes using constant-time comparison to prevent timing attacks
    return secrets.compare_digest(computed_hash, stored_password_hash)


def hash_password_legacy(password: str) -> bytes:
    """
    Legacy password hashing for backward compatibility.
    Used to migrate old passwords that were stored as plain bytes.
    
    This function converts plain text passwords to bytes for comparison
    with old password storage format.
    
    Args:
        password: Plain text password
    
    Returns:
        bytes: Password as UTF-8 bytes
    
    Note:
        This is only for migration purposes. New passwords should use hash_password().
    """
    return password.encode('utf-8')

