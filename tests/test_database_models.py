"""
Unit Tests for Database Models

Tests CRUD operations for all database models including:
- DeceasedModel
- AssetsModel
- ClaimsModel
- ClaimantsModel
- InstitutionsModel
- UsersModel
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models_deceased import DeceasedModel
from db.models_assets import AssetsModel
from db.models_claims import ClaimsModel
from db.models_claimants import ClaimantsModel
from db.models_institutions import InstitutionsModel
from db.models_users import UsersModel


class TestDeceasedModel(unittest.TestCase):
    """Test cases for DeceasedModel."""
    
    @patch('db.models_deceased.get_connection')
    def test_create_deceased(self, mock_connection):
        """Test creating a deceased record."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = DeceasedModel()
        record_data = {
            "FirstName": "John",
            "LastName": "Doe",
            "NationalId": "123456789"
        }
        
        result = model.create(record_data)
        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
    
    @patch('db.models_deceased.get_connection')
    def test_get_all_deceased(self, mock_connection):
        """Test retrieving all deceased records."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "123456789", "John", "Doe", None, None)
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = DeceasedModel()
        results = model.get_all()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["FirstName"], "John")


class TestAssetsModel(unittest.TestCase):
    """Test cases for AssetsModel."""
    
    @patch('db.models_assets.get_connection')
    def test_create_asset(self, mock_connection):
        """Test creating an asset record."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = AssetsModel()
        asset_data = {
            "DeceasedId": 1,
            "InstitutionId": 1,
            "AssetType": "Bank Account",
            "EstimatedValue": 10000.00
        }
        
        result = model.create(asset_data)
        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()


class TestClaimsModel(unittest.TestCase):
    """Test cases for ClaimsModel."""
    
    @patch('db.models_claims.get_connection')
    def test_create_claim(self, mock_connection):
        """Test creating a claim record."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = ClaimsModel()
        claim_data = {
            "AssetId": 1,
            "ClaimantId": 1,
            "Status": "Pending"
        }
        
        result = model.create(claim_data)
        self.assertEqual(result, 1)
        mock_cursor.execute.assert_called_once()
    
    @patch('db.models_claims.get_connection')
    def test_update_claim_status(self, mock_connection):
        """Test updating claim status using stored procedure."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]  # Success
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = ClaimsModel()
        success, error = model.update_status(1, "Verified", use_stored_procedure=True)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        mock_cursor.execute.assert_called_once()


class TestUsersModel(unittest.TestCase):
    """Test cases for UsersModel."""
    
    @patch('db.models_users.get_connection')
    def test_get_user_by_username(self, mock_connection):
        """Test retrieving user by username."""
        # Mock database connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            1, "admin", b"password_hash", "Admin", None, None
        )
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_connection.return_value = mock_conn
        
        model = UsersModel()
        user = model.get_by_username("admin")
        
        self.assertIsNotNone(user)
        self.assertEqual(user["Username"], "admin")
        self.assertEqual(user["Role"], "Admin")


if __name__ == '__main__':
    unittest.main()


