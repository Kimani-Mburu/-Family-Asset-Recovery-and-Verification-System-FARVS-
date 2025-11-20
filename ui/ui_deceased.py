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

# Import database operations
from db.db_operations import db_ops
from auth.session import get_current_user
from ui.theme import stripe_treeview
from logging_config import get_logger

logger = get_logger(__name__)


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
    
    def __init__(self, parent: tk.Tk, container: Optional[ttk.Frame] = None):
        """
        Initialize the deceased records management window.
        
        Args:
            parent: Parent Tkinter window
            container: Optional container frame (if provided, use instead of Toplevel)
        """
        self.parent = parent
        # Use provided container or create Toplevel
        if container:
            self.window = container
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Deceased Records Management")
            self.window.geometry("900x700")
            self.window.minsize(800, 600)
        
        # Data storage
        self.current_record: Optional[Dict[str, Any]] = None
        self.records: List[Dict[str, Any]] = []
        
        self._setup_ui()
        # Load records after UI is set up (use after() to ensure UI is ready)
        self.window.after(100, self._load_records)
    
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
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        
        # Form fields container - Use ScrollableFrame for scrolling support
        from ui.scrollable_frame import ScrollableFrame
        form_fields_container = ScrollableFrame(form_frame)
        form_fields_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Create form fields in the inner_frame of ScrollableFrame
        self._create_form_fields(form_fields_container.inner_frame)
        
        # Right panel - Records list with view toggle
        list_frame = ttk.LabelFrame(main_frame, text="Records List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        # CRITICAL: Configure list_frame for proper expansion
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Search and view toggle
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # View toggle buttons
        view_frame = ttk.Frame(search_frame)
        view_frame.grid(row=0, column=2, sticky=tk.E)
        
        self.view_mode = tk.StringVar(value="table")
        ttk.Radiobutton(view_frame, text="📋 Table", variable=self.view_mode,
                       value="table", command=self._toggle_view).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(view_frame, text="🃏 Cards", variable=self.view_mode,
                       value="cards", command=self._toggle_view).pack(side=tk.LEFT, padx=2)
        
        # Records display container - CRITICAL: Must have proper grid weights
        self.records_container = ttk.Frame(list_frame)
        self.records_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.records_container.columnconfigure(0, weight=1)
        self.records_container.rowconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Records treeview (default)
        self._create_records_treeview(self.records_container)
        
        # Card view (hidden by default)
        self.card_view_frame = None
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_action_buttons(actions_frame)
    
    def _create_form_fields(self, parent: ttk.Frame):
        """Create form input fields for deceased record data with date pickers and required indicators."""
        from ui.components import DatePicker, create_tooltip
        
        # National ID
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="National ID:").pack(side=tk.LEFT)
        self.national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(parent, textvariable=self.national_id_var, width=25)
        national_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(national_id_entry, "Optional: National identification number")
        
        # First Name (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="First Name:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(parent, textvariable=self.first_name_var, width=25)
        first_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(first_name_entry, "Required: First name of the deceased person")
        
        # Middle Name
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Middle Name:").pack(side=tk.LEFT)
        self.middle_name_var = tk.StringVar()
        middle_name_entry = ttk.Entry(parent, textvariable=self.middle_name_var, width=25)
        middle_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(middle_name_entry, "Optional: Middle name of the deceased person")
        
        # Last Name (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Last Name:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(parent, textvariable=self.last_name_var, width=25)
        last_name_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(last_name_entry, "Required: Last name of the deceased person")
        
        # Gender
        ttk.Label(parent, text="Gender:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(parent, textvariable=self.gender_var, width=22, state="readonly",
                                    values=["", "Male", "Female", "Other", "Prefer not to say"])
        gender_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(gender_combo, "Optional: Gender")
        
        # Date of Birth (with date picker)
        self.dob_picker = DatePicker(parent, "Date of Birth:", required=False)
        self.dob_picker.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        create_tooltip(self.dob_picker.entry, "Optional: Date of birth (YYYY-MM-DD)")
        self.dob_var = self.dob_picker.value
        
        # Date of Death (with date picker)
        self.dod_picker = DatePicker(parent, "Date of Death:", required=False)
        self.dod_picker.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        create_tooltip(self.dod_picker.entry, "Optional: Date of death (YYYY-MM-DD)")
        self.dod_var = self.dod_picker.value
        
        # Additional Information Section
        section_label = ttk.Label(parent, text="Additional Information", font=("Segoe UI", 10, "bold"))
        section_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Address
        ttk.Label(parent, text="Address:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        address_entry = ttk.Entry(parent, textvariable=self.address_var, width=25)
        address_entry.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(address_entry, "Optional: Last known address")
        
        # Place of Birth
        ttk.Label(parent, text="Place of Birth:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.place_of_birth_var = tk.StringVar()
        place_of_birth_entry = ttk.Entry(parent, textvariable=self.place_of_birth_var, width=25)
        place_of_birth_entry.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(place_of_birth_entry, "Optional: City, State/Province, Country")
        
        # Place of Death
        ttk.Label(parent, text="Place of Death:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.place_of_death_var = tk.StringVar()
        place_of_death_entry = ttk.Entry(parent, textvariable=self.place_of_death_var, width=25)
        place_of_death_entry.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(place_of_death_entry, "Optional: City, State/Province, Country")
        
        # Occupation
        ttk.Label(parent, text="Occupation:").grid(row=11, column=0, sticky=tk.W, pady=5)
        self.occupation_var = tk.StringVar()
        occupation_entry = ttk.Entry(parent, textvariable=self.occupation_var, width=25)
        occupation_entry.grid(row=11, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(occupation_entry, "Optional: Last known occupation")
        
        # Marital Status
        ttk.Label(parent, text="Marital Status:").grid(row=12, column=0, sticky=tk.W, pady=5)
        self.marital_status_var = tk.StringVar()
        marital_status_combo = ttk.Combobox(parent, textvariable=self.marital_status_var, width=22, state="readonly",
                                             values=["", "Single", "Married", "Divorced", "Widowed"])
        marital_status_combo.grid(row=12, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(marital_status_combo, "Optional: Marital status")
        
        # Next of Kin
        ttk.Label(parent, text="Next of Kin:").grid(row=13, column=0, sticky=tk.W, pady=5)
        self.next_of_kin_var = tk.StringVar()
        next_of_kin_entry = ttk.Entry(parent, textvariable=self.next_of_kin_var, width=25)
        next_of_kin_entry.grid(row=13, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(next_of_kin_entry, "Optional: Primary contact person")
        
        # Death Certificate Number
        ttk.Label(parent, text="Death Certificate #:").grid(row=14, column=0, sticky=tk.W, pady=5)
        self.death_cert_var = tk.StringVar()
        death_cert_entry = ttk.Entry(parent, textvariable=self.death_cert_var, width=25)
        death_cert_entry.grid(row=14, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(death_cert_entry, "Optional: Official death certificate number")
        
        # Notes
        ttk.Label(parent, text="Notes:").grid(row=15, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(parent, width=25, height=3)
        self.notes_text.grid(row=15, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(self.notes_text, "Optional: Additional information or remarks")
        
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
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.tree, tree_frame)
        
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
        """Load deceased records from database and populate the display."""
        try:
            # Load from database using stored procedure
            records = db_ops.get_deceased_with_assets()
            # Convert to expected format (map column names)
            self.records = []
            for row in records:
                record = {
                    "DeceasedId": row.get("DeceasedId"),
                    "NationalId": row.get("NationalId"),
                    "FirstName": row.get("FirstName"),
                    "MiddleName": row.get("MiddleName"),
                    "LastName": row.get("LastName"),
                    "Gender": row.get("Gender"),
                    "DateOfBirth": row.get("DateOfBirth"),
                    "DateOfDeath": row.get("DateOfDeath"),
                    "PlaceOfBirth": row.get("PlaceOfBirth"),
                    "PlaceOfDeath": row.get("PlaceOfDeath"),
                    "Address": row.get("Address"),
                    "Occupation": row.get("Occupation"),
                    "MaritalStatus": row.get("MaritalStatus"),
                    "NextOfKin": row.get("NextOfKin"),
                    "DeathCertificateNumber": row.get("DeathCertificateNumber"),
                    "Notes": row.get("Notes"),
                    "CreatedAt": row.get("CreatedAt"),
                    "AssetCount": row.get("AssetCount", 0),
                    "TotalAssetValue": row.get("TotalAssetValue", 0)
                }
                self.records.append(record)
            logger.info(f"Loaded {len(self.records)} deceased records from database")
            
            # Ensure records_container exists
            if not hasattr(self, 'records_container'):
                logger.warning("records_container not initialized yet")
                return
            
            # Show empty state if no records
            if not self.records:
                from ui.components import EmptyState
                # Clear display area
                for widget in self.records_container.winfo_children():
                    widget.destroy()
                EmptyState.show(
                    self.records_container,
                    "No deceased records found",
                    "Add New Record",
                    self._add_record
                )
                return
            
            # Update display based on view mode
            self._update_display()
                
        except Exception as e:
            import traceback
            error_msg = f"Failed to load records: {e}"
            logger.error(f"Error in _load_records: {error_msg}", exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _toggle_view(self):
        """Toggle between table and card view."""
        self._update_display()
    
    def _update_display(self):
        """Update display based on current view mode."""
        # Clear container
        for widget in self.records_container.winfo_children():
            widget.destroy()
        
        if self.view_mode.get() == "cards":
            self._display_cards()
        else:
            self._display_table()
    
    def _display_table(self):
        """Display records in table view."""
        # Always recreate treeview to ensure it's in the right container
        self._create_records_treeview(self.records_container)
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate treeview
        for record in self.records:
            values = (
                record["DeceasedId"],
                record["NationalId"] or "",
                record["FirstName"],
                record["LastName"],
                record["DateOfBirth"] or "",
                record["DateOfDeath"] or ""
            )
            self.tree.insert("", tk.END, values=values)
        
        # Zebra striping
        stripe_treeview(self.tree)
                
    def _display_cards(self):
        """Display records in card view."""
        from ui.record_display import RecordGridView
        
        # Create card view frame (recreate each time to avoid conflicts)
        self.card_view_frame = ttk.Frame(self.records_container)
        self.card_view_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.records_container.columnconfigure(0, weight=1)
        self.records_container.rowconfigure(0, weight=1)
        self.card_view_frame.columnconfigure(0, weight=1)
        self.card_view_frame.rowconfigure(0, weight=1)
        
        # Create grid view
        grid_view = RecordGridView(
            self.card_view_frame,
            card_type="deceased",
            columns=3,
            on_select=self._on_card_select
        )
        grid_view.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Display records
        grid_view.display_records(self.records)
        self.current_grid_view = grid_view
    
    def _on_card_select(self, record: Dict[str, Any]):
        """Handle card selection."""
        self.current_record = record
        self._populate_form(record)
    
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
        self.national_id_var.set(record.get("NationalId", "") or "")
        self.first_name_var.set(record.get("FirstName", ""))
        self.middle_name_var.set(record.get("MiddleName", "") or "")
        self.last_name_var.set(record.get("LastName", ""))
        self.gender_var.set(record.get("Gender", "") or "")
        dob = record.get("DateOfBirth", "")
        if dob:
            self.dob_var.set(str(dob)[:10] if len(str(dob)) > 10 else str(dob))
        else:
            self.dob_var.set("")
        dod = record.get("DateOfDeath", "")
        if dod:
            self.dod_var.set(str(dod)[:10] if len(str(dod)) > 10 else str(dod))
        else:
            self.dod_var.set("")
        self.address_var.set(record.get("Address", "") or "")
        self.place_of_birth_var.set(record.get("PlaceOfBirth", "") or "")
        self.place_of_death_var.set(record.get("PlaceOfDeath", "") or "")
        self.occupation_var.set(record.get("Occupation", "") or "")
        self.marital_status_var.set(record.get("MaritalStatus", "") or "")
        self.next_of_kin_var.set(record.get("NextOfKin", "") or "")
        self.death_cert_var.set(record.get("DeathCertificateNumber", "") or "")
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(1.0, record.get("Notes", "") or "")
    
    def _on_search_change(self, *args):
        """Handle search text change to filter records."""
        search_text = self.search_var.get().lower()
        
        # Filter records
        filtered_records = [
            r for r in self.records
            if (search_text in r["FirstName"].lower() or 
                search_text in r["LastName"].lower() or
                (r["NationalId"] and search_text in r["NationalId"].lower()))
        ]
        
        # Update display with filtered records
        if self.view_mode.get() == "cards":
            if hasattr(self, 'current_grid_view'):
                self.current_grid_view.display_records(filtered_records)
        else:
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Populate with filtered records
            for record in filtered_records:
                values = (
                    record["DeceasedId"],
                    record["NationalId"] or "",
                    record["FirstName"],
                    record["LastName"],
                    record["DateOfBirth"] or "",
                    record["DateOfDeath"] or ""
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
        dob = self.dob_picker.get() if hasattr(self, 'dob_picker') else self.dob_var.get().strip()
        if dob and dob != "YYYY-MM-DD":
            try:
                datetime.datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Birth must be in YYYY-MM-DD format.")
                return False
        
        dod = self.dod_picker.get() if hasattr(self, 'dod_picker') else self.dod_var.get().strip()
        if dod and dod != "YYYY-MM-DD":
            try:
                datetime.datetime.strptime(dod, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Date of Death must be in YYYY-MM-DD format.")
                return False
        
        return True
    
    def _add_record(self):
        """Add a new deceased record using modal."""
        from ui.modals import AddDeceasedModal
        
        def on_save(record_data):
            """Handle save from modal."""
            try:
                # Convert date strings to datetime objects if needed
                date_of_birth = None
                date_of_death = None
                if record_data.get("DateOfBirth"):
                    if isinstance(record_data["DateOfBirth"], str):
                        date_of_birth = datetime.datetime.strptime(record_data["DateOfBirth"], "%Y-%m-%d").date()
                    else:
                        date_of_birth = record_data["DateOfBirth"]
                if record_data.get("DateOfDeath"):
                    if isinstance(record_data["DateOfDeath"], str):
                        date_of_death = datetime.datetime.strptime(record_data["DateOfDeath"], "%Y-%m-%d").date()
                    else:
                        date_of_death = record_data["DateOfDeath"]
                
                # Get user ID for audit
                user = get_current_user()
                user_id = user["UserId"] if user else None
                
                # DB create using stored procedure (audit is automatic)
                success, new_id, error = db_ops.create_deceased_with_validation(
                    first_name=record_data["FirstName"],
                    last_name=record_data["LastName"],
                    national_id=record_data.get("NationalId"),
                    middle_name=record_data.get("MiddleName"),
                    gender=record_data.get("Gender"),
                    date_of_birth=date_of_birth,
                    date_of_death=date_of_death,
                    place_of_birth=record_data.get("PlaceOfBirth"),
                    place_of_death=record_data.get("PlaceOfDeath"),
                    address=record_data.get("Address"),
                    occupation=record_data.get("Occupation"),
                    marital_status=record_data.get("MaritalStatus"),
                    next_of_kin=record_data.get("NextOfKin"),
                    death_certificate_number=record_data.get("DeathCertificateNumber"),
                    notes=record_data.get("Notes"),
                    user_id=user_id
                )
                
                if success:
                    messagebox.showinfo("Success", "Deceased record added successfully.")
                    self._load_records()
                else:
                    messagebox.showerror("Error", f"Failed to add record: {error}")
            except Exception as e:
                logger.error(f"Error creating deceased record: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to add record: {e}")
        
        # Show modal
        modal = AddDeceasedModal(self.window, on_save)
        modal.show()
    
    def _update_record(self):
        """Update the selected deceased record."""
        if not self.current_record:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        
        if not self._validate_form():
            return
        
        try:
            # Get date values from date pickers
            dob_str = self.dob_picker.get() if hasattr(self, 'dob_picker') else self.dob_var.get().strip() or None
            dod_str = self.dod_picker.get() if hasattr(self, 'dod_picker') else self.dod_var.get().strip() or None
            
            # Convert date strings to datetime objects if needed
            dob_value = None
            dod_value = None
            if dob_str and dob_str != "YYYY-MM-DD":
                try:
                    dob_value = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid Date of Birth format.")
                    return
            if dod_str and dod_str != "YYYY-MM-DD":
                try:
                    dod_value = datetime.datetime.strptime(dod_str, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Error", "Invalid Date of Death format.")
                    return
            
            # Get user ID for audit
            user = get_current_user()
            user_id = user["UserId"] if user else None
            
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            # DB update using stored procedure (audit is automatic)
            success, error = db_ops.update_deceased_record(
                deceased_id=self.current_record["DeceasedId"],
                first_name=self.first_name_var.get().strip(),
                last_name=self.last_name_var.get().strip(),
                national_id=self.national_id_var.get().strip() or None,
                middle_name=self.middle_name_var.get().strip() or None,
                gender=self.gender_var.get().strip() or None,
                date_of_birth=dob_value,
                date_of_death=dod_value,
                place_of_birth=self.place_of_birth_var.get().strip() or None,
                place_of_death=self.place_of_death_var.get().strip() or None,
                address=self.address_var.get().strip() or None,
                occupation=self.occupation_var.get().strip() or None,
                marital_status=self.marital_status_var.get().strip() or None,
                next_of_kin=self.next_of_kin_var.get().strip() or None,
                death_certificate_number=self.death_cert_var.get().strip() or None,
                notes=notes if notes else None,
                user_id=user_id
            )
            
            if success:
                messagebox.showinfo("Success", "Record updated successfully.")
                self._load_records()
            else:
                messagebox.showerror("Error", f"Failed to update record: {error}")
            
        except Exception as e:
            logger.error(f"Error updating deceased record: {e}", exc_info=True)
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
            # Get user ID for audit
            user = get_current_user()
            user_id = user["UserId"] if user else None
            
            # DB delete using stored procedure (audit is automatic)
            success, error = db_ops.delete_deceased_record(
                deceased_id=self.current_record["DeceasedId"],
                user_id=user_id
            )
            
            if success:
                messagebox.showinfo("Success", "Record deleted successfully.")
                self._clear_form()
                self._load_records()
            else:
                messagebox.showerror("Error", f"Failed to delete record: {error}")
            
        except Exception as e:
            logger.error(f"Error deleting deceased record: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to delete record: {e}")
    
    def _clear_form(self):
        """Clear all form fields."""
        self.national_id_var.set("")
        self.first_name_var.set("")
        self.middle_name_var.set("")
        self.last_name_var.set("")
        self.gender_var.set("")
        self.dob_var.set("")
        self.dod_var.set("")
        self.address_var.set("")
        self.place_of_birth_var.set("")
        self.place_of_death_var.set("")
        self.occupation_var.set("")
        self.marital_status_var.set("")
        self.next_of_kin_var.set("")
        self.death_cert_var.set("")
        self.notes_text.delete(1.0, tk.END)
        
        self.current_record = None
        
        # Clear treeview selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
