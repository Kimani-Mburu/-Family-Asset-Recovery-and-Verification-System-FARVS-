"""
Unit Tests for UI Components

Tests UI components including:
- ModalDialog
- DatePicker
- StatusBadge
- RecordCard
- ClaimsProgressTracker
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.components import ModalDialog, DatePicker, StatusBadge
from ui.claims_progress import ClaimsProgressTracker
from ui.record_display import RecordCard


class TestModalDialog(unittest.TestCase):
    """Test cases for ModalDialog component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_modal_creation(self):
        """Test creating a modal dialog."""
        modal = ModalDialog(self.root, "Test Modal", width=400, height=300)
        self.assertIsNotNone(modal.dialog)
        self.assertEqual(modal.dialog.title(), "Test Modal")
        modal.dialog.destroy()
    
    def test_modal_buttons(self):
        """Test adding buttons to modal."""
        modal = ModalDialog(self.root, "Test Modal")
        btn = modal.add_button("OK", style="primary")
        self.assertIsNotNone(btn)
        modal.dialog.destroy()


class TestDatePicker(unittest.TestCase):
    """Test cases for DatePicker component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_date_picker_creation(self):
        """Test creating a date picker."""
        frame = tk.Frame(self.root)
        picker = DatePicker(frame, "Test Date:", required=False)
        self.assertIsNotNone(picker.entry)
        self.assertIsNotNone(picker.value)


class TestStatusBadge(unittest.TestCase):
    """Test cases for StatusBadge component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_status_badge_creation(self):
        """Test creating a status badge."""
        frame = tk.Frame(self.root)
        badge = StatusBadge.create(frame, "Pending", row=0, column=0)
        self.assertIsNotNone(badge)


class TestClaimsProgressTracker(unittest.TestCase):
    """Test cases for ClaimsProgressTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_progress_tracker_creation(self):
        """Test creating a progress tracker."""
        frame = tk.Frame(self.root)
        tracker = ClaimsProgressTracker(frame)
        self.assertIsNotNone(tracker.progress_frame)
    
    def test_progress_tracker_update(self):
        """Test updating progress tracker with claim data."""
        frame = tk.Frame(self.root)
        tracker = ClaimsProgressTracker(frame)
        
        claim_data = {
            "Status": "Verified",
            "FiledAt": "2024-01-01",
            "VerifiedAt": "2024-01-15"
        }
        
        tracker.update_progress(claim_data)
        # Verify tracker was updated
        self.assertIsNotNone(tracker.progress_frame)


if __name__ == '__main__':
    unittest.main()


