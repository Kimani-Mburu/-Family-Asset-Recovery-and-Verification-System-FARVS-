"""
FARVS Main Application Entry Point
===================================

This module provides the main Tkinter application window with navigation
to all FARVS modules (Deceased, Assets, Claims, Reports).

Structure:
- MainWindow: Primary application container with menu/navigation
- Module launchers: Functions to open each module window
- Error handling: Database connection validation on startup
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from typing import Optional

# Import database connection utilities
from db.db_connect import try_connect
from config import get_env


class MainWindow:
    """
    Main application window providing navigation to all FARVS modules.
    
    Features:
    - Database connection status indicator
    - Module navigation buttons
    - About dialog
    - Error handling for database connectivity issues
    """
    
    def __init__(self):
        """Initialize the main application window."""
        self.root = tk.Tk()
        self.root.title("Family Asset Recovery and Verification System (FARVS)")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Database connection status
        self.db_connected = False
        self.db_error: Optional[str] = None
        
        self._setup_ui()
        self._check_database_connection()
    
    def _setup_ui(self):
        """Create and layout the main user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Family Asset Recovery and Verification System",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Database status
        self.status_frame = ttk.LabelFrame(main_frame, text="Database Status", padding="10")
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.status_label = ttk.Label(self.status_frame, text="Checking connection...")
        self.status_label.grid(row=0, column=0)
        
        # Module navigation
        nav_frame = ttk.LabelFrame(main_frame, text="System Modules", padding="10")
        nav_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Navigation buttons
        buttons = [
            ("Deceased Records", self._open_deceased_module),
            ("Asset Management", self._open_assets_module),
            ("Claims Processing", self._open_claims_module),
            ("Reports & Analytics", self._open_reports_module)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, command=command, width=20)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure button grid
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.columnconfigure(1, weight=1)
        
        # System info
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        server_info = f"Server: {get_env('DB_SERVER', 'Not configured')}"
        db_info = f"Database: {get_env('DB_NAME', 'Not configured')}"
        
        ttk.Label(info_frame, text=server_info).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=db_info).grid(row=1, column=0, sticky=tk.W)
        
        # Menu bar
        self._create_menu()
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About FARVS", command=self._show_about)
    
    def _check_database_connection(self):
        """Test database connectivity and update status display."""
        try:
            self.db_connected, self.db_error = try_connect()
            
            if self.db_connected:
                self.status_label.config(text="✓ Connected to database", foreground="green")
            else:
                self.status_label.config(text=f"✗ Database error: {self.db_error}", foreground="red")
                
        except Exception as e:
            self.db_connected = False
            self.db_error = str(e)
            self.status_label.config(text=f"✗ Connection failed: {self.db_error}", foreground="red")
    
    def _open_deceased_module(self):
        """Launch the Deceased Records management module."""
        if not self.db_connected:
            messagebox.showerror("Database Error", "Cannot connect to database. Please check your configuration.")
            return
        
        try:
            # Import here to avoid circular imports
            from ui.ui_deceased import DeceasedWindow
            DeceasedWindow(self.root)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Deceased module not available: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Deceased module: {e}")
    
    def _open_assets_module(self):
        """Launch the Asset Management module."""
        if not self.db_connected:
            messagebox.showerror("Database Error", "Cannot connect to database. Please check your configuration.")
            return
        
        try:
            from ui.ui_assets import AssetsWindow
            AssetsWindow(self.root)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Assets module not available: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Assets module: {e}")
    
    def _open_claims_module(self):
        """Launch the Claims Processing module."""
        if not self.db_connected:
            messagebox.showerror("Database Error", "Cannot connect to database. Please check your configuration.")
            return
        
        try:
            from ui.ui_claims import ClaimsWindow
            ClaimsWindow(self.root)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Claims module not available: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Claims module: {e}")
    
    def _open_reports_module(self):
        """Launch the Reports & Analytics module."""
        if not self.db_connected:
            messagebox.showerror("Database Error", "Cannot connect to database. Please check your configuration.")
            return
        
        try:
            from ui.ui_reports import ReportsWindow
            ReportsWindow(self.root)
        except ImportError as e:
            messagebox.showerror("Module Error", f"Reports module not available: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Reports module: {e}")
    
    def _show_about(self):
        """Display application information dialog."""
        about_text = """
Family Asset Recovery and Verification System (FARVS)

Version: 1.0.0
Database: Microsoft SQL Server
Interface: Python Tkinter

This system enables families to trace, verify, and claim 
unclaimed assets of deceased relatives through a comprehensive 
database management interface.

Developed for Database Systems Group Project
        """
        messagebox.showinfo("About FARVS", about_text.strip())
    
    def run(self):
        """Start the main application event loop."""
        self.root.mainloop()


def main():
    """
    Application entry point.
    
    Initializes the main window and starts the Tkinter event loop.
    Handles any startup errors gracefully.
    """
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Fatal error starting FARVS: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
