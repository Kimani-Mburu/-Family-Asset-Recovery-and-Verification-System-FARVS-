"""
FARVS Deceased Records Management Module
=======================================

This module provides CRUD operations for managing deceased person records
in the FARVS database through a Tkinter interface.

Structure:
- DeceasedWindow: Main window class for deceased records management
- Form handling: Add, edit, delete deceased records
- Data validation: Input validation and error handling
- Database integration: Uses models_deceased for data operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import datetime

# Import database models
from db.models_deceased import DeceasedModel
from db.models_audit import AuditLogModel
from auth.session import get_current_user
from ui.theme import stripe_treeview


class DeceasedWindow:
    """
    Tkinter window for managing deceased person records.
    
    Features:
    - Add new deceased records
    - Edit existing records
    - Delete records (with confirmation)
    - Search and filter records
    - Data validation
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize the deceased records management window.
        
        Args:
            parent: Parent Tkinter window
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Deceased Records Management")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        
        # Data storage
        self.current_record: Optional[Dict[str, Any]] = None
        self.records: List[Dict[str, Any]] = []
        
        # Initialize database models
        self.model = DeceasedModel()
        self.audit = AuditLogModel()
        
        self._setup_ui()
        self._load_records()
    
    def _setup_ui(self):
        """Create and layout the user interface components."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Form
        form_frame = ttk.LabelFrame(main_frame, text="Deceased Record Form", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Form fields
        self._create_form_fields(form_frame)
        
        # Right panel - Records list
        list_frame = ttk.LabelFrame(main_frame, text="Records List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Search and filter
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Records treeview
        self._create_records_treeview(list_frame)
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_action_buttons(actions_frame)
    
    def _create_form_fields(self, parent: ttk.Frame):
        """Create form input fields for deceased record data."""
        # National ID
        ttk.Label(parent, text="National ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(parent, textvariable=self.national_id_var, width=25)
        national_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # First Name
        ttk.Label(parent, text="First Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(parent, textvariable=self.first_name_var, width=25)
        first_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Last Name
        ttk.Label(parent, text="Last Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(parent, textvariable=self.last_name_var, width=25)
        last_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Date of Birth
        ttk.Label(parent, text="Date of Birth:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.dob_var = tk.StringVar()
        dob_entry = ttk.Entry(parent, textvariable=self.dob_var, width=25)
        dob_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(parent, text="(YYYY-MM-DD)", font=("Arial", 8)).grid(row=3, column=2, sticky=tk.W, padx=(5, 0))
        
        # Date of Death
        ttk.Label(parent, text="Date of Death:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.dod_var = tk.StringVar()
        dod_entry = ttk.Entry(parent, textvariable=self.dod_var, width=25)
        dod_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(parent, text="(YYYY-MM-DD)", font=("Arial", 8)).grid(row=4, column=2, sticky=tk.W, padx=(5, 0))
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_records_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying records."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "National ID", "First Name", "Last Name", "DOB", "DOD")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "National ID": 100, "First Name": 120, "Last Name": 120, "DOB": 100, "DOD": 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_record_select)
    
    def _create_action_buttons(self, parent: ttk.Frame):
        """Create action buttons for CRUD operations."""
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        ttk.Button(btn_frame, text="Add New", command=self._add_record, width=12).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Update", command=self._update_record, width=12).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._delete_record, width=12).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self._clear_form, width=12).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_records, width=12).grid(row=0, column=4, padx=2)
    
    def _load_records(self):
        """Load deceased records from database and populate the treeview."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load from database
            self.records = self.model.get_all()
            
            # Populate treeview
            for record in self.records:
                values = (
                    record["DeceasedId"],
                    record["NationalId"],
                    record["FirstName"],
                    record["LastName"],
                    record["DateOfBirth"],
                    record["DateOfDeath"]
                )
                self.tree.insert("", tk.END, values=values)
            # Zebra striping
            stripe_treeview(self.tree)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {e}")
    
    def _on_record_select(self, event):
        """Handle record selection in treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected record data
        item = self.tree.item(selection[0])
        record_id = item['values'][0]
        
        # Find record in data
        self.current_record = next((r for r in self.records if r["DeceasedId"] == record_id), None)
        
        if self.current_record:
            self._populate_form(self.current_record)
    
    def _populate_form(self, record: Dict[str, Any]):
        """Populate form fields with record data."""
        self.national_id_var.set(record.get("NationalId", ""))
        self.first_name_var.set(record.get("FirstName", ""))
        self.last_name_var.set(record.get("LastName", ""))
        self.dob_var.set(record.get("DateOfBirth", ""))
        self.dod_var.set(record.get("DateOfDeath", ""))
    
    def _on_search_change(self, *args):
        """Handle search text change to filter records."""
        search_text = self.search_var.get().lower()
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display matching records
        for record in self.records:
            if (search_text in record["FirstName"].lower() or 
                search_text in record["LastName"].lower() or
                search_text in record["NationalId"].lower()):
                
                values = (
                    record["DeceasedId"],
                    record["NationalId"],
                    record["FirstName"],
                    record["LastName"],
                    record["DateOfBirth"],
                    record["DateOfDeath"]
                )
                self.tree.insert("", tk.END, values=values)
        stripe_treeview(self.tree)
    
    def _validate_form(self) -> bool:
        """Validate form input data."""
        # Required fields
        if not self.first_name_var.get().strip():
            messagebox.showerror("Validation Error", "First Name is required.")
            return False
        
        if not self.last_name_var.get().strip():
            messagebox.showerror("Validation Error", "Last Name is required.")
            return False
        
        # Date validation
        dob = self.dob_var.get().strip()
        if dob:
            try:
                datetime.datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Birth must be in YYYY-MM-DD format.")
                return False
        
        dod = self.dod_var.get().strip()
        if dod:
            try:
                datetime.datetime.strptime(dod, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Death must be in YYYY-MM-DD format.")
                return False
        
        return True
    
    def _add_record(self):
        """Add a new deceased record."""
        if not self._validate_form():
            return
        
        try:
            # Prepare record data
            record_data = {
                "NationalId": self.national_id_var.get().strip() or None,
                "FirstName": self.first_name_var.get().strip(),
                "LastName": self.last_name_var.get().strip(),
                "DateOfBirth": self.dob_var.get().strip() or None,
                "DateOfDeath": self.dod_var.get().strip() or None
            }
            
            # DB create
            new_id = self.model.create(record_data)
            # Audit
            user = get_current_user()
            self.audit.write(user_id=user["UserId"] if user else None, action="CREATE", entity="Deceased", entity_id=str(new_id), details=f"Created deceased {record_data['FirstName']} {record_data['LastName']}", ip=None)
            
            messagebox.showinfo("Success", "Deceased record added successfully.")
            self._clear_form()
            self._load_records()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add record: {e}")
    
    def _update_record(self):
        """Update the selected deceased record."""
        if not self.current_record:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        
        if not self._validate_form():
            return
        
        try:
            # Prepare updated data
            updated_data = {
                "DeceasedId": self.current_record["DeceasedId"],
                "NationalId": self.national_id_var.get().strip() or None,
                "FirstName": self.first_name_var.get().strip(),
                "LastName": self.last_name_var.get().strip(),
                "DateOfBirth": self.dob_var.get().strip() or None,
                "DateOfDeath": self.dod_var.get().strip() or None
            }
            
            # DB update
            ok = self.model.update(updated_data["DeceasedId"], updated_data)
            if ok:
                user = get_current_user()
                self.audit.write(user_id=user["UserId"] if user else None, action="UPDATE", entity="Deceased", entity_id=str(updated_data["DeceasedId"]), details="Updated deceased record", ip=None)
            
            messagebox.showinfo("Success", "Record updated successfully.")
            self._load_records()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")
    
    def _delete_record(self):
        """Delete the selected deceased record."""
        if not self.current_record:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return
        
        # Confirmation dialog
        name = f"{self.current_record['FirstName']} {self.current_record['LastName']}"
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the record for {name}?"):
            return
        
        try:
            # DB delete
            ok = self.model.delete(self.current_record["DeceasedId"])
            if ok:
                user = get_current_user()
                self.audit.write(user_id=user["UserId"] if user else None, action="DELETE", entity="Deceased", entity_id=str(self.current_record["DeceasedId"]), details=f"Deleted {name}", ip=None)
            
            messagebox.showinfo("Success", "Record deleted successfully.")
            self._clear_form()
            self._load_records()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")
    
    def _clear_form(self):
        """Clear all form fields."""
        self.national_id_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.dob_var.set("")
        self.dod_var.set("")
        self.current_record = None
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
