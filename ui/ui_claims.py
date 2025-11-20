"""
FARVS Claims Processing Module
==============================

This module provides CRUD operations for managing claims and claimants
in the FARVS database through a Tkinter interface.

Structure:
- ClaimsWindow: Main window class for claims management
- Claimant management: Add, edit, delete claimant records
- Claims processing: Link claims to assets and claimants
- Status tracking: Pending, Verified, Settled workflow
- Data validation: Input validation and relationship integrity
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import datetime

# Import database models
from db.models_claims import ClaimsModel
from db.models_claimants import ClaimantsModel
from db.models_assets import AssetsModel
from db.models_cases import CasesModel, TasksModel, StatusHistoryModel
from db.models_audit import AuditLogModel
from auth.session import get_current_user
from ui.theme import stripe_treeview
from logging_config import get_logger

logger = get_logger(__name__)


class ClaimsWindow:
    """
    Tkinter window for managing claims and claimants.
    
    Features:
    - Add new claimants
    - Create claims linked to assets and claimants
    - Update claim status (Pending → Verified → Settled)
    - Track claim processing timeline
    - Search and filter claims
    - Relationship validation
    """
    
    def __init__(self, parent: tk.Tk, container: Optional[ttk.Frame] = None):
        """
        Initialize the claims processing window.
        
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
            self.window.title("Claims Processing")
            self.window.geometry("1200x800")
            self.window.minsize(1000, 700)
        
        # Data storage
        self.current_claim: Optional[Dict[str, Any]] = None
        self.current_claimant: Optional[Dict[str, Any]] = None
        self.claims: List[Dict[str, Any]] = []
        self.claimants: List[Dict[str, Any]] = []
        self.assets: List[Dict[str, Any]] = []
        
        # Initialize database models
        self.claims_model = ClaimsModel()
        self.claimants_model = ClaimantsModel()
        self.assets_model = AssetsModel()
        self.cases_model = CasesModel()
        self.tasks_model = TasksModel()
        self.status_history = StatusHistoryModel()
        self.audit = AuditLogModel()
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Create and layout the user interface components."""
        # If container is provided (embedded mode), use it directly
        # Otherwise create a notebook for standalone mode
        if hasattr(self, 'window') and isinstance(self.window, ttk.Frame):
            # Embedded mode - use container directly with a notebook inside
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            
            notebook = ttk.Notebook(self.window)
            notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            
            # Claims tab
            claims_frame = ttk.Frame(notebook)
            notebook.add(claims_frame, text="Claims Management")
            self._setup_claims_tab(claims_frame)
            
            # Claimants tab
            claimants_frame = ttk.Frame(notebook)
            notebook.add(claimants_frame, text="Claimants Management")
            self._setup_claimants_tab(claimants_frame)
        else:
            # Standalone mode - create notebook in Toplevel
            notebook = ttk.Notebook(self.window)
            notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            
            # Configure grid weights
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            
            # Claims tab
            claims_frame = ttk.Frame(notebook)
            notebook.add(claims_frame, text="Claims Management")
            self._setup_claims_tab(claims_frame)
            
            # Claimants tab
            claimants_frame = ttk.Frame(notebook)
            notebook.add(claimants_frame, text="Claimants Management")
            self._setup_claimants_tab(claimants_frame)
    
    def _setup_claims_tab(self, parent: ttk.Frame):
        """Setup the claims management tab with progress tracking."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Claim form with progress tracking
        form_frame = ttk.LabelFrame(main_frame, text="Create/Manage Claim", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Progress tracking section (initially hidden, shown when claim is selected/created)
        self.progress_frame = ttk.LabelFrame(form_frame, text="Claim Progress & Timeline", padding="10")
        self.progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(0, weight=1)
        self.progress_tracker = None
        self._create_progress_placeholder()
        
        # Form fields container - Use ScrollableFrame for scrolling support
        from ui.scrollable_frame import ScrollableFrame
        form_fields_container = ScrollableFrame(form_frame)
        form_fields_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        form_frame.rowconfigure(1, weight=1)
        form_frame.columnconfigure(0, weight=1)
        # Create form fields in the inner_frame of ScrollableFrame
        self._create_claim_form_fields(form_fields_container.inner_frame)
        
        # Right panel - Claims list with view toggle
        list_frame = ttk.LabelFrame(main_frame, text="Claims List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        # CRITICAL: Configure list_frame for proper expansion
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Search, filter, and view toggle
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.claims_search_var = tk.StringVar()
        self.claims_search_var.trace('w', self._on_claims_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.claims_search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # Status filter
        ttk.Label(search_frame, text="Status:").grid(row=0, column=2, padx=(10, 5))
        self.status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var, width=15, state="readonly")
        status_combo['values'] = ('All', 'Pending', 'Verified', 'Settled')
        status_combo.set('All')
        status_combo.bind('<<ComboboxSelected>>', self._on_status_filter_change)
        status_combo.grid(row=0, column=3, padx=(0, 10))
        
        # View toggle buttons
        view_frame = ttk.Frame(search_frame)
        view_frame.grid(row=0, column=4, sticky=tk.E)
        
        self.claims_view_mode = tk.StringVar(value="table")
        ttk.Radiobutton(view_frame, text="📋 Table", variable=self.claims_view_mode,
                       value="table", command=self._toggle_claims_view).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(view_frame, text="🃏 Cards", variable=self.claims_view_mode,
                       value="cards", command=self._toggle_claims_view).pack(side=tk.LEFT, padx=2)
        
        # Claims display container - CRITICAL: Must have proper grid weights
        self.claims_container = ttk.Frame(list_frame)
        self.claims_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.claims_container.columnconfigure(0, weight=1)
        self.claims_container.rowconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Claims treeview (default)
        self._create_claims_treeview(self.claims_container)
        
        # Add empty state handling
        self.claims_list_frame = list_frame
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_claims_action_buttons(actions_frame)
    
    def _setup_claimants_tab(self, parent: ttk.Frame):
        """Setup the claimants management tab."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Claimant form
        form_frame = ttk.LabelFrame(main_frame, text="Claimant Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        
        # Form fields container - Use ScrollableFrame for scrolling support
        from ui.scrollable_frame import ScrollableFrame
        form_fields_container = ScrollableFrame(form_frame)
        form_fields_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Create form fields in the inner_frame of ScrollableFrame
        self._create_claimant_form_fields(form_fields_container.inner_frame)
        
        # Right panel - Claimants list
        list_frame = ttk.LabelFrame(main_frame, text="Claimants List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Search
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.claimants_search_var = tk.StringVar()
        self.claimants_search_var.trace('w', self._on_claimants_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.claimants_search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Claimants treeview
        self._create_claimants_treeview(list_frame)
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_claimants_action_buttons(actions_frame)
    
    def _create_progress_placeholder(self):
        """Create placeholder message for progress tracker."""
        # Clear any existing widgets
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        # Show placeholder message
        placeholder = ttk.Label(
            self.progress_frame,
            text="Create or select a claim to view progress",
            font=("Segoe UI", 10),
            foreground="#6B7280"
        )
        placeholder.grid(row=0, column=0, pady=20)
        self.progress_frame.columnconfigure(0, weight=1)
    
    def _create_complete_progress_tracker(self):
        """Create complete progress tracker with timeline."""
        from ui.claims_progress import ClaimsProgressTracker
        
        # Clear placeholder
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        # Create progress tracker instance
        self.progress_tracker = ClaimsProgressTracker(self.progress_frame)
    
    def _update_progress_tracker(self, claim_data: Dict[str, Any]):
        """Update progress tracker with claim data."""
        logger.debug(f"Updating progress tracker with claim data: Status={claim_data.get('Status')}, FiledAt={claim_data.get('FiledAt')}, VerifiedAt={claim_data.get('VerifiedAt')}, SettledAt={claim_data.get('SettledAt')}")
        # Create tracker if it doesn't exist
        if not self.progress_tracker:
            logger.debug("Creating progress tracker")
            self._create_complete_progress_tracker()
        
        # Update with claim data
        if self.progress_tracker:
            logger.debug("Calling progress_tracker.update_progress()")
            self.progress_tracker.update_progress(claim_data)
            logger.debug("Progress tracker updated")
        else:
            logger.warning("Progress tracker is None, cannot update")
    
    def _create_claim_form_fields(self, parent: ttk.Frame):
        """Create form input fields for claim data."""
        from ui.components import create_tooltip
        
        # Asset Selection
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Asset:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.asset_var = tk.StringVar()
        self.asset_combo = ttk.Combobox(parent, textvariable=self.asset_var, width=25, state="readonly")
        self.asset_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(self.asset_combo, "Required: Select the asset for this claim")
        
        # Claimant Selection
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Claimant:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.claimant_var = tk.StringVar()
        self.claimant_combo = ttk.Combobox(parent, textvariable=self.claimant_var, width=25, state="readonly")
        self.claimant_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(self.claimant_combo, "Required: Select the claimant for this claim")
        
        # Status
        ttk.Label(parent, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(parent, textvariable=self.status_var, width=25, state="readonly")
        status_combo['values'] = ('Pending', 'Verified', 'Settled')
        status_combo.set('Pending')
        status_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        # Status change will update progress when claim is saved
        create_tooltip(status_combo, "Current status of the claim")
        
        # Notes
        ttk.Label(parent, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(parent, width=25, height=4)
        self.notes_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(self.notes_text, "Optional: Additional notes about the claim")
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_claimant_form_fields(self, parent: ttk.Frame):
        """Create form input fields for claimant data with enhanced fields."""
        from ui.components import DatePicker, create_tooltip
        
        row = 0
        
        # Personal Information Section
        section_label = ttk.Label(parent, text="Personal Information", font=("Segoe UI", 10, "bold"))
        section_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # National ID
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="National ID:").pack(side=tk.LEFT)
        self.claimant_national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(parent, textvariable=self.claimant_national_id_var, width=25)
        national_id_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(national_id_entry, "Optional: National identification number")
        row += 1
        
        # First Name (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="First Name:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.claimant_first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(parent, textvariable=self.claimant_first_name_var, width=25)
        first_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(first_name_entry, "Required: First name of the claimant")
        row += 1
        
        # Middle Name
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="Middle Name:").pack(side=tk.LEFT)
        self.claimant_middle_name_var = tk.StringVar()
        middle_name_entry = ttk.Entry(parent, textvariable=self.claimant_middle_name_var, width=25)
        middle_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(middle_name_entry, "Optional: Middle name of the claimant")
        row += 1
        
        # Last Name (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="Last Name:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.claimant_last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(parent, textvariable=self.claimant_last_name_var, width=25)
        last_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(last_name_entry, "Required: Last name of the claimant")
        row += 1
        
        # Date of Birth
        self.claimant_dob_picker = DatePicker(parent, "Date of Birth:", required=False)
        self.claimant_dob_picker.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.claimant_dob_var = self.claimant_dob_picker.value
        create_tooltip(self.claimant_dob_picker.entry, "Optional: Date of birth for verification")
        row += 1
        
        # Gender
        ttk.Label(parent, text="Gender:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(parent, textvariable=self.claimant_gender_var, width=22, state="readonly",
                                    values=["", "Male", "Female", "Other", "Prefer not to say"])
        gender_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(gender_combo, "Optional: Gender")
        row += 1
        
        # Relationship
        ttk.Label(parent, text="Relationship:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.relationship_var = tk.StringVar()
        relationship_combo = ttk.Combobox(parent, textvariable=self.relationship_var, width=22)
        relationship_combo['values'] = ('Spouse', 'Child', 'Parent', 'Sibling', 'Other Relative', 'Executor', 'Other')
        relationship_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(relationship_combo, "Relationship to the deceased person")
        row += 1
        
        # Contact Information Section
        section_label2 = ttk.Label(parent, text="Contact Information", font=("Segoe UI", 10, "bold"))
        section_label2.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Email
        ttk.Label(parent, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_email_var = tk.StringVar()
        email_entry = ttk.Entry(parent, textvariable=self.claimant_email_var, width=25)
        email_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(email_entry, "Email address for communication")
        row += 1
        
        # Phone
        ttk.Label(parent, text="Phone:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_phone_var = tk.StringVar()
        phone_entry = ttk.Entry(parent, textvariable=self.claimant_phone_var, width=25)
        phone_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(phone_entry, "Phone number (include country code if international)")
        row += 1
        
        # Contact (General)
        ttk.Label(parent, text="Contact:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(parent, textvariable=self.contact_var, width=25)
        contact_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(contact_entry, "General contact information")
        row += 1
        
        # Address
        ttk.Label(parent, text="Address:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_address_var = tk.StringVar()
        address_entry = ttk.Entry(parent, textvariable=self.claimant_address_var, width=25)
        address_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(address_entry, "Street, City, State, ZIP, Country")
        row += 1
        
        # Additional Information Section
        section_label3 = ttk.Label(parent, text="Additional Information", font=("Segoe UI", 10, "bold"))
        section_label3.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Occupation
        ttk.Label(parent, text="Occupation:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_occupation_var = tk.StringVar()
        occupation_entry = ttk.Entry(parent, textvariable=self.claimant_occupation_var, width=25)
        occupation_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(occupation_entry, "Current occupation")
        row += 1
        
        # Marital Status
        ttk.Label(parent, text="Marital Status:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_marital_status_var = tk.StringVar()
        marital_status_combo = ttk.Combobox(parent, textvariable=self.claimant_marital_status_var, width=22, state="readonly",
                                            values=["", "Single", "Married", "Divorced", "Widowed"])
        marital_status_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(marital_status_combo, "Optional: Marital status")
        row += 1
        
        # Alternate Contact
        ttk.Label(parent, text="Alternate Contact:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_alternate_contact_var = tk.StringVar()
        alternate_contact_entry = ttk.Entry(parent, textvariable=self.claimant_alternate_contact_var, width=25)
        alternate_contact_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(alternate_contact_entry, "Backup contact person")
        row += 1
        
        # Relationship Proof
        ttk.Label(parent, text="Relationship Proof:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_relationship_proof_var = tk.StringVar()
        relationship_proof_entry = ttk.Entry(parent, textvariable=self.claimant_relationship_proof_var, width=25)
        relationship_proof_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(relationship_proof_entry, "Document reference proving relationship")
        row += 1
        
        # Notes
        ttk.Label(parent, text="Notes:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.claimant_notes_text = tk.Text(parent, width=25, height=3)
        self.claimant_notes_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        create_tooltip(self.claimant_notes_text, "Additional information or remarks")
        row += 1
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_claims_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying claims."""
        logger.debug("Creating claims treeview with proper scrolling pattern")
        
        # Container frame - MUST use grid for parent
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for proper scrolling
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "Asset", "Claimant", "Status", "Filed Date", "Notes")
        self.claims_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "Asset": 200, "Claimant": 150, "Status": 80, "Filed Date": 100, "Notes": 150}
        for col in columns:
            self.claims_tree.heading(col, text=col)
            self.claims_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claims_tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.claims_tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.claims_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.claims_tree, tree_frame)
        
        # Bind selection event
        self.claims_tree.bind("<<TreeviewSelect>>", self._on_claim_select)
        
        logger.debug("Claims treeview created successfully")
    
    def _create_claimants_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying claimants."""
        logger.debug("Creating claimants treeview with proper scrolling pattern")
        
        # Container frame - MUST use grid for parent
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Treeview columns
        columns = ("ID", "National ID", "First Name", "Last Name", "Relationship", "Contact")
        self.claimants_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "National ID": 100, "First Name": 120, "Last Name": 120, "Relationship": 100, "Contact": 150}
        for col in columns:
            self.claimants_tree.heading(col, text=col)
            self.claimants_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claimants_tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.claimants_tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.claimants_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.claimants_tree, tree_frame)
        
        # Bind selection event
        self.claimants_tree.bind("<<TreeviewSelect>>", self._on_claimant_select)
        
        logger.debug("Claimants treeview created successfully")
    
    def _create_claims_action_buttons(self, parent: ttk.Frame):
        """Create action buttons for claims CRUD operations."""
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        ttk.Button(btn_frame, text="Add Claim", command=self._add_claim, width=12).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Update Status", command=self._update_claim_status, width=12).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete Claim", command=self._delete_claim, width=12).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self._clear_claim_form, width=12).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_data, width=12).grid(row=0, column=4, padx=2)
    
    def _create_claimants_action_buttons(self, parent: ttk.Frame):
        """Create action buttons for claimants CRUD operations."""
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        ttk.Button(btn_frame, text="Add Claimant", command=self._add_claimant, width=12).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Update", command=self._update_claimant, width=12).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._delete_claimant, width=12).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self._clear_claimant_form, width=12).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_data, width=12).grid(row=0, column=4, padx=2)
    
    def _load_data(self):
        """Load all required data from database."""
        try:
            # Load claimants
            self._load_claimants()
            
            # Load assets
            self._load_assets()
            
            # Load claims
            self._load_claims()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def _load_claimants(self):
        """Load claimants for the dropdown and list."""
        try:
            # Load from DB
            self.claimants = self.claimants_model.get_all()
            
            # Update combobox
            claimant_names = [f"{c['FirstName']} {c['LastName']}" for c in self.claimants]
            self.claimant_combo['values'] = claimant_names
            
            # Update claimants treeview
            self._refresh_claimants_treeview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load claimants: {e}")
    
    def _load_assets(self):
        """Load assets for the dropdown."""
        try:
            # Load from DB
            self.assets = self.assets_model.get_all_with_details()
            
            # Update combobox
            asset_names = [f"{a['AssetType']} - {a['Identifier']} ({a['DeceasedName']})" for a in self.assets]
            self.asset_combo['values'] = asset_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load assets: {e}")
    
    def _load_claims(self):
        """Load claims from database and populate the treeview."""
        try:
            # Load from DB first
            self.claims = self.claims_model.get_all_with_details()
            logger.info(f"Loaded {len(self.claims)} claims from database")
            
            # Ensure claims_container exists before trying to refresh
            if not hasattr(self, 'claims_container'):
                logger.warning("claims_container not initialized yet, skipping display")
                return
            
            # Clear existing items only if treeview exists
            if hasattr(self, 'claims_tree') and self.claims_tree.winfo_exists():
                try:
                    for item in self.claims_tree.get_children():
                        self.claims_tree.delete(item)
                except tk.TclError:
                    # Widget was destroyed, will be recreated
                    pass
            
            # Populate treeview
            self._refresh_claims_treeview()
                
        except Exception as e:
            logger.error(f"Error in _load_claims: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load claims: {e}")
    
    def _refresh_claims_treeview(self):
        """Refresh the claims display with current data."""
        try:
            # Ensure we have claims data
            if not hasattr(self, 'claims') or not self.claims:
                self.claims = []
            
            # Filter by status if selected
            if hasattr(self, 'status_filter_var'):
                status_filter = self.status_filter_var.get()
            else:
                status_filter = 'All'
            
            filtered_claims = self.claims
            if status_filter != 'All':
                filtered_claims = [c for c in self.claims if c.get('Status') == status_filter]
            
            # Show empty state if no claims
            if not filtered_claims:
                from ui.components import EmptyState
                for widget in self.claims_container.winfo_children():
                    widget.destroy()
                EmptyState.show(
                    self.claims_container,
                    "No claims found",
                    "Add New Claim",
                    self._add_claim
                )
                return
            
            # Update display based on view mode
            self._update_claims_display(filtered_claims)
        except Exception as e:
            logger.error(f"Error in _refresh_claims_treeview: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to refresh claims display: {e}")
    
    def _toggle_claims_view(self):
        """Toggle between table and card view for claims."""
        self._refresh_claims_treeview()
    
    def _update_claims_display(self, filtered_claims: List[Dict[str, Any]]):
        """Update claims display based on view mode."""
        try:
            # Clear container
            for widget in self.claims_container.winfo_children():
                widget.destroy()
            
            # Get view mode, default to table if not set
            if hasattr(self, 'claims_view_mode'):
                view_mode = self.claims_view_mode.get()
            else:
                view_mode = "table"
            
            if view_mode == "cards":
                self._display_claims_cards(filtered_claims)
            else:
                self._display_claims_table(filtered_claims)
        except Exception as e:
            logger.error(f"Error in _update_claims_display: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to update claims display: {e}")
    
    def _display_claims_table(self, filtered_claims: List[Dict[str, Any]]):
        """Display claims in table view."""
        try:
            # Always recreate treeview to ensure it's in the right container
            self._create_claims_treeview(self.claims_container)
            
            # Clear existing items (treeview is fresh, but clear anyway for safety)
            try:
                for item in self.claims_tree.get_children():
                    self.claims_tree.delete(item)
            except (tk.TclError, AttributeError):
                # Widget might not be ready yet, continue anyway
                pass
            
            # Populate treeview
            logger.debug(f"Displaying {len(filtered_claims)} claims in table view")
            for claim in filtered_claims:
                values = (
                    claim.get("ClaimId", ""),
                    claim.get("AssetName", ""),
                    claim.get("ClaimantName", ""),
                    claim.get("Status", ""),
                    str(claim.get("FiledAt", ""))[:10] if claim.get("FiledAt") else "",
                    (claim.get("Notes", "")[:50] + "...") if claim.get("Notes") and len(claim.get("Notes", "")) > 50 else (claim.get("Notes") or "")
                )
                item = self.claims_tree.insert("", tk.END, values=values)
                self.claims_tree.set(item, "Status", claim.get("Status", ""))
            stripe_treeview(self.claims_tree)
        except Exception as e:
            logger.error(f"Error in _display_claims_table: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to display claims table: {e}")
    
    def _display_claims_cards(self, filtered_claims: List[Dict[str, Any]]):
        """Display claims in card view."""
        from ui.record_display import RecordGridView
        
        # Create card view frame with grid layout for proper scrolling
        card_view_frame = ttk.Frame(self.claims_container)
        card_view_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.claims_container.columnconfigure(0, weight=1)
        self.claims_container.rowconfigure(0, weight=1)
        card_view_frame.columnconfigure(0, weight=1)
        card_view_frame.rowconfigure(0, weight=1)
        
        # Create grid view
        grid_view = RecordGridView(
            card_view_frame,
            card_type="claim",
            columns=3,
            on_select=self._on_claim_card_select
        )
        grid_view.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Display records
        grid_view.display_records(filtered_claims)
        self.current_claims_grid_view = grid_view
    
    def _on_claim_card_select(self, record: Dict[str, Any]):
        """Handle claim card selection."""
        self.current_claim = record
        self._populate_claim_form(record)
    
    def _refresh_claimants_treeview(self):
        """Refresh the claimants treeview with current data."""
        # Clear existing items
        for item in self.claimants_tree.get_children():
            self.claimants_tree.delete(item)
        
        # Populate treeview
        for claimant in self.claimants:
            values = (
                claimant["ClaimantId"],
                claimant["NationalId"],
                claimant["FirstName"],
                claimant["LastName"],
                claimant["Relationship"],
                claimant["Contact"]
            )
            self.claimants_tree.insert("", tk.END, values=values)
        stripe_treeview(self.claimants_tree)
    
    def _on_claim_select(self, event):
        """Handle claim selection in treeview."""
        try:
            if not hasattr(self, 'claims_tree') or not self.claims_tree.winfo_exists():
                return
            selection = self.claims_tree.selection()
            if not selection:
                return
            
            # Get selected claim data
            item = self.claims_tree.item(selection[0])
            claim_id = item['values'][0]
            
            # Find claim in data
            self.current_claim = next((c for c in self.claims if c["ClaimId"] == claim_id), None)
            
            if self.current_claim:
                self._populate_claim_form(self.current_claim)
                # Update progress tracker with full claim data
                self._update_progress_tracker(self.current_claim)
        except (tk.TclError, AttributeError, KeyError, IndexError):
            # Widget might have been destroyed or selection invalid
            return
    
    def _on_claimant_select(self, event):
        """Handle claimant selection in treeview."""
        selection = self.claimants_tree.selection()
        if not selection:
            return
        
        # Get selected claimant data
        item = self.claimants_tree.item(selection[0])
        claimant_id = item['values'][0]
        
        # Find claimant in data
        self.current_claimant = next((c for c in self.claimants if c["ClaimantId"] == claimant_id), None)
        
        if self.current_claimant:
            self._populate_claimant_form(self.current_claimant)
    
    def _populate_claim_form(self, claim: Dict[str, Any]):
        """Populate claim form fields with claim data."""
        # Set asset - need to match the format used in combobox
        asset_id = claim.get("AssetId")
        for asset in self.assets:
            if asset["AssetId"] == asset_id:
                asset_display = f"{asset['AssetType']} - {asset['Identifier']} ({asset['DeceasedName']})"
                self.asset_var.set(asset_display)
                break
        
        # Set claimant - need to match the format used in combobox
        claimant_id = claim.get("ClaimantId")
        for claimant in self.claimants:
            if claimant["ClaimantId"] == claimant_id:
                claimant_display = f"{claimant['FirstName']} {claimant['LastName']}"
                self.claimant_var.set(claimant_display)
                break
        
        # Set status
        status = claim.get("Status", "Pending")
        self.status_var.set(status)
        
        # Update progress tracker with full claim data
        self._update_progress_tracker(claim)
        
        # Set notes
        self.notes_text.delete(1.0, tk.END)
        notes = claim.get("Notes", "")
        if notes:
            self.notes_text.insert(1.0, notes)
    
    def _populate_claimant_form(self, claimant: Dict[str, Any]):
        """Populate claimant form fields with claimant data."""
        self.claimant_national_id_var.set(claimant.get("NationalId", "") or "")
        self.claimant_first_name_var.set(claimant.get("FirstName", ""))
        self.claimant_middle_name_var.set(claimant.get("MiddleName", "") or "")
        self.claimant_last_name_var.set(claimant.get("LastName", ""))
        dob = claimant.get("DateOfBirth", "")
        if dob:
            self.claimant_dob_var.set(str(dob)[:10] if len(str(dob)) > 10 else str(dob))
        else:
            self.claimant_dob_var.set("")
        self.claimant_gender_var.set(claimant.get("Gender", "") or "")
        self.relationship_var.set(claimant.get("Relationship", "") or "")
        self.contact_var.set(claimant.get("Contact", "") or "")
        
        self.claimant_email_var.set(claimant.get("Email", "") or "")
        self.claimant_phone_var.set(claimant.get("Phone", "") or "")
        self.claimant_address_var.set(claimant.get("Address", "") or "")
        self.claimant_occupation_var.set(claimant.get("Occupation", "") or "")
        self.claimant_marital_status_var.set(claimant.get("MaritalStatus", "") or "")
        self.claimant_alternate_contact_var.set(claimant.get("AlternateContact", "") or "")
        self.claimant_relationship_proof_var.set(claimant.get("RelationshipProof", "") or "")
        self.claimant_notes_text.delete(1.0, tk.END)
        self.claimant_notes_text.insert(1.0, claimant.get("Notes", "") or "")
    
    def _on_claims_search_change(self, *args):
        """Handle search text change to filter claims."""
        search_text = self.claims_search_var.get().lower()
        
        # Filter claims by search text
        filtered_claims = [
            c for c in self.claims
            if (search_text in str(c["ClaimId"]).lower() or
                search_text in c["AssetName"].lower() or 
                search_text in c["ClaimantName"].lower() or
                search_text in c["Status"].lower() or
                (c.get("Notes") and search_text in c["Notes"].lower()))
        ]
        
        # Apply status filter
        status_filter = self.status_filter_var.get()
        if status_filter != 'All':
            filtered_claims = [c for c in filtered_claims if c['Status'] == status_filter]
        
        # Update display with filtered claims
        self._update_claims_display(filtered_claims)
    
    def _on_claimants_search_change(self, *args):
        """Handle search text change to filter claimants."""
        search_text = self.claimants_search_var.get().lower()
        
        # Clear treeview
        for item in self.claimants_tree.get_children():
            self.claimants_tree.delete(item)
        
        # Filter and display matching claimants
        for claimant in self.claimants:
            if (search_text in claimant["FirstName"].lower() or 
                search_text in claimant["LastName"].lower() or
                search_text in claimant["NationalId"].lower() or
                search_text in claimant["Relationship"].lower()):
                
                values = (
                    claimant["ClaimantId"],
                    claimant["NationalId"],
                    claimant["FirstName"],
                    claimant["LastName"],
                    claimant["Relationship"],
                    claimant["Contact"]
                )
                self.claimants_tree.insert("", tk.END, values=values)
    
    def _on_status_filter_change(self, *args):
        """Handle status filter change."""
        # Apply search filter first
        search_text = self.claims_search_var.get().lower()
        filtered_claims = [
            c for c in self.claims
            if (search_text in str(c["ClaimId"]).lower() or
                search_text in c["AssetName"].lower() or 
                search_text in c["ClaimantName"].lower() or
                search_text in c["Status"].lower() or
                (c.get("Notes") and search_text in c["Notes"].lower()))
        ]
        
        # Apply status filter
        status_filter = self.status_filter_var.get()
        if status_filter != 'All':
            filtered_claims = [c for c in filtered_claims if c['Status'] == status_filter]
        
        # Update display
        self._update_claims_display(filtered_claims)
    
    def _validate_claim_form(self) -> bool:
        """Validate claim form input data."""
        if not self.asset_var.get().strip():
            messagebox.showerror("Validation Error", "Please select an asset.")
            return False
        
        if not self.claimant_var.get().strip():
            messagebox.showerror("Validation Error", "Please select a claimant.")
            return False
        
        return True
    
    def _validate_claimant_form(self) -> bool:
        """Validate claimant form input data."""
        if not self.claimant_first_name_var.get().strip():
            messagebox.showerror("Validation Error", "First Name is required.")
            return False
        
        if not self.claimant_last_name_var.get().strip():
            messagebox.showerror("Validation Error", "Last Name is required.")
            return False
        
        return True
    
    def _get_selected_asset_id(self) -> Optional[int]:
        """Get the selected asset ID."""
        asset_name = self.asset_var.get()
        if not asset_name:
            return None
        
        for asset in self.assets:
            if f"{asset['AssetType']} - {asset['Identifier']} ({asset['DeceasedName']})" == asset_name:
                return asset["AssetId"]
        return None
    
    def _get_selected_claimant_id(self) -> Optional[int]:
        """Get the selected claimant ID."""
        claimant_name = self.claimant_var.get()
        if not claimant_name:
            return None
        
        for claimant in self.claimants:
            if f"{claimant['FirstName']} {claimant['LastName']}" == claimant_name:
                return claimant["ClaimantId"]
        return None
    
    def _add_claim(self):
        """Add a new claim record."""
        # If a claim is already selected, clear it first to prevent duplicates
        if self.current_claim:
            response = messagebox.askyesno(
                "Clear Current Selection",
                "A claim is currently selected. Do you want to clear it and create a new claim?"
            )
            if response:
                self._clear_claim_form()
            else:
                return
        
        if not self._validate_claim_form():
            return
        
        try:
            # Get selected IDs
            asset_id = self._get_selected_asset_id()
            claimant_id = self._get_selected_claimant_id()
            
            if not asset_id or not claimant_id:
                messagebox.showerror("Error", "Invalid selection for asset or claimant.")
                return
            
            # Prepare claim data
            claim_data = {
                "AssetId": asset_id,
                "ClaimantId": claimant_id,
                "Status": self.status_var.get(),
                "Notes": self.notes_text.get(1.0, tk.END).strip()
            }
            
            # DB create
            new_id = self.claims_model.create(claim_data)
            # Create a case and initial task
            user = get_current_user()
            case_id = self.cases_model.create(title=f"Claim #{new_id}", description=claim_data["Notes"], claim_id=new_id, created_by_user_id=(user["UserId"] if user else None))
            self.tasks_model.add(case_id=case_id, title="Initial review", status="Pending", assigned_to_user_id=(user["UserId"] if user else None))
            # Audit and status history
            self.status_history.add(entity_type="Claim", entity_id=new_id, status=claim_data["Status"], notes="Claim created", changed_by_user_id=(user["UserId"] if user else None))
            self.audit.write(user_id=(user["UserId"] if user else None), action="CREATE", entity="Claim", entity_id=str(new_id), details=f"Created claim for asset {asset_id} by claimant {claimant_id}", ip=None)
            
            messagebox.showinfo("Success", "Claim added successfully.")
            
            # Load the newly created claim to show progress
            updated_claims = self.claims_model.get_all_with_details()
            new_claim = next((c for c in updated_claims if c["ClaimId"] == new_id), None)
            if new_claim:
                self.current_claim = new_claim
                self._populate_claim_form(new_claim)
                self._update_progress_tracker(new_claim)
            else:
                self._clear_claim_form()
            
            self._load_claims()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add claim: {e}")
    
    def _add_claimant(self):
        """Add a new claimant record using modal."""
        from ui.modals import AddClaimantModal
        
        def on_save(claimant_data):
            """Handle save from modal."""
            try:
                # DB create
                new_id = self.claimants_model.create(claimant_data)
                # Audit
                user = get_current_user()
                self.audit.write(
                    user_id=user["UserId"] if user else None,
                    action="CREATE",
                    entity="Claimant",
                    entity_id=str(new_id),
                    details=f"Created claimant {claimant_data['FirstName']} {claimant_data['LastName']}",
                    ip=None
                )
                
                messagebox.showinfo("Success", "Claimant added successfully.")
                self._load_claimants()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add claimant: {e}")
        
        # Show modal
        modal = AddClaimantModal(self.window, on_save)
        modal.show()
    
    def _update_claim_status(self):
        """Update the selected claim status."""
        logger.info("Updating claim status")
        if not self.current_claim:
            logger.warning("No claim selected for update")
            messagebox.showwarning("No Selection", "Please select a claim to update.")
            return
        
        try:
            logger.debug(f"Current claim: {self.current_claim.get('ClaimId')}, Current status: {self.current_claim.get('Status')}")
            logger.debug(f"New status from form: {self.status_var.get()}")
            # Prepare updated data
            updated_data = {
                "ClaimId": self.current_claim["ClaimId"],
                "AssetId": self.current_claim["AssetId"],
                "ClaimantId": self.current_claim["ClaimantId"],
                "Status": self.status_var.get(),
                "Notes": self.notes_text.get(1.0, tk.END).strip()
            }
            
            # Add verification/settlement dates based on status
            if updated_data["Status"] == "Verified" and self.current_claim["Status"] != "Verified":
                updated_data["VerifiedAt"] = datetime.date.today().strftime("%Y-%m-%d")
            elif updated_data["Status"] == "Settled" and self.current_claim["Status"] != "Settled":
                updated_data["SettledAt"] = datetime.date.today().strftime("%Y-%m-%d")
            
            # Update claim status using stored procedure (with transaction and audit)
            user = get_current_user()
            notes_text = self.notes_text.get(1.0, tk.END).strip()
            logger.debug(f"Calling update_status with claim_id={updated_data['ClaimId']}, status={updated_data['Status']}")
            success, error = self.claims_model.update_status(
                claim_id=updated_data["ClaimId"],
                status=updated_data["Status"],
                notes=notes_text if notes_text else None,
                use_stored_procedure=False  # Use direct UPDATE to avoid stored procedure issues
            )
            
            logger.debug(f"Update result: success={success}, error={error}")
            if success:
                logger.info(f"Claim {updated_data['ClaimId']} status updated to {updated_data['Status']}")
                messagebox.showinfo("Success", "Claim status updated successfully.")
                self._load_claims()
                # Reload current claim to refresh form and progress tracker
                if self.current_claim:
                    claim_id = self.current_claim["ClaimId"]
                    # Get fresh data from database
                    updated_claims = self.claims_model.get_all_with_details()
                    self.current_claim = next((c for c in updated_claims if c["ClaimId"] == claim_id), None)
                    if self.current_claim:
                        logger.debug(f"Refreshed claim data: Status={self.current_claim.get('Status')}, FiledAt={self.current_claim.get('FiledAt')}, VerifiedAt={self.current_claim.get('VerifiedAt')}, SettledAt={self.current_claim.get('SettledAt')}")
                        # CRITICAL: Update status_var first to match database
                        self.status_var.set(self.current_claim.get("Status", "Pending"))
                        # Populate form with updated data
                        self._populate_claim_form(self.current_claim)
                        # Force update progress tracker with fresh claim data
                        logger.debug("Updating progress tracker with refreshed claim data")
                        self._update_progress_tracker(self.current_claim)
                    else:
                        logger.warning(f"Could not find updated claim with ID {claim_id}")
            else:
                logger.error(f"Failed to update claim status: {error or 'Unknown error'}")
                messagebox.showerror("Error", f"Failed to update claim status: {error or 'Unknown error'}")
            
        except Exception as e:
            logger.exception(f"Exception while updating claim status: {e}")
            messagebox.showerror("Error", f"Failed to update claim: {e}")
    
    def _update_claimant(self):
        """Update the selected claimant record."""
        if not self.current_claimant:
            messagebox.showwarning("No Selection", "Please select a claimant to update.")
            return
        
        if not self._validate_claimant_form():
            return
        
        try:
            # Get date value from date picker
            dob_value = self.claimant_dob_picker.get() if hasattr(self, 'claimant_dob_picker') else self.claimant_dob_var.get().strip() or None
            if dob_value and dob_value != "YYYY-MM-DD":
                dob_value = dob_value
            else:
                dob_value = None
            notes = self.claimant_notes_text.get(1.0, tk.END).strip()
            
            # Prepare updated data
            updated_data = {
                "ClaimantId": self.current_claimant["ClaimantId"],
                "NationalId": self.claimant_national_id_var.get().strip() or None,
                "FirstName": self.claimant_first_name_var.get().strip(),
                "MiddleName": self.claimant_middle_name_var.get().strip() or None,
                "LastName": self.claimant_last_name_var.get().strip(),
                "DateOfBirth": dob_value,
                "Gender": self.claimant_gender_var.get().strip() or None,
                "Relationship": self.relationship_var.get().strip() or None,
                "Contact": self.contact_var.get().strip() or None,
                "Email": self.claimant_email_var.get().strip() or None,
                "Phone": self.claimant_phone_var.get().strip() or None,
                "Address": self.claimant_address_var.get().strip() or None,
                "Occupation": self.claimant_occupation_var.get().strip() or None,
                "MaritalStatus": self.claimant_marital_status_var.get().strip() or None,
                "AlternateContact": self.claimant_alternate_contact_var.get().strip() or None,
                "RelationshipProof": self.claimant_relationship_proof_var.get().strip() or None,
                "Notes": notes if notes else None
            }
            
            # DB update
            self.claimants_model.update(updated_data["ClaimantId"], updated_data)
            user = get_current_user()
            self.audit.write(user_id=(user["UserId"] if user else None), action="UPDATE", entity="Claimant", entity_id=str(updated_data["ClaimantId"]), details="Updated claimant", ip=None)
            
            messagebox.showinfo("Success", "Claimant updated successfully.")
            self._load_claimants()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update claimant: {e}")
    
    def _delete_claim(self):
        """Delete the selected claim record."""
        if not self.current_claim:
            messagebox.showwarning("No Selection", "Please select a claim to delete.")
            return
        
        # Confirmation dialog
        claim_info = f"Claim #{self.current_claim['ClaimId']} - {self.current_claim['AssetName']}"
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete: {claim_info}?"):
            return
        
        try:
            # DB delete
            claim_id = self.current_claim["ClaimId"]
            self.claims_model.delete(claim_id)
            user = get_current_user()
            self.audit.write(user_id=(user["UserId"] if user else None), action="DELETE", entity="Claim", entity_id=str(claim_id), details="Deleted claim", ip=None)
            
            messagebox.showinfo("Success", "Claim deleted successfully.")
            self._clear_claim_form()
            self._load_claims()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete claim: {e}")
    
    def _delete_claimant(self):
        """Delete the selected claimant record."""
        if not self.current_claimant:
            messagebox.showwarning("No Selection", "Please select a claimant to delete.")
            return
        
        # Check if claimant has associated claims
        associated_claims = [c for c in self.claims if c["ClaimantId"] == self.current_claimant["ClaimantId"]]
        if associated_claims:
            messagebox.showerror("Cannot Delete", f"Cannot delete claimant with {len(associated_claims)} associated claims.")
            return
        
        # Confirmation dialog
        claimant_name = f"{self.current_claimant['FirstName']} {self.current_claimant['LastName']}"
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete claimant: {claimant_name}?"):
            return
        
        try:
            # Delete claimant from database
            claimant_id = self.current_claimant["ClaimantId"]
            success = self.claimants_model.delete(claimant_id)
            
            if success:
                # Log audit entry
                user = get_current_user()
                if user:
                    self.audit.write(
                        user_id=user.get('UserId'),
                        action='DELETE',
                        entity='Claimant',
                        entity_id=str(claimant_id),
                        details=f"Deleted claimant: {claimant_name}",
                        ip=None
                    )
                
                messagebox.showinfo("Success", "Claimant deleted successfully.")
                self._clear_claimant_form()
                self._load_claimants()
            else:
                messagebox.showerror("Error", "Failed to delete claimant. Claimant may have associated claims.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete claimant: {e}")
    
    def _clear_claim_form(self):
        """Clear all claim form fields."""
        self.asset_var.set("")
        self.claimant_var.set("")
        self.status_var.set("Pending")
        self.notes_text.delete(1.0, tk.END)
        self.current_claim = None
        
        # Clear treeview selection
        try:
            if hasattr(self, 'claims_tree') and self.claims_tree.winfo_exists():
                for item in self.claims_tree.selection():
                    self.claims_tree.selection_remove(item)
        except (tk.TclError, AttributeError):
            pass
    
    def _clear_claimant_form(self):
        """Clear all claimant form fields."""
        self.claimant_national_id_var.set("")
        self.claimant_first_name_var.set("")
        self.claimant_middle_name_var.set("")
        self.claimant_last_name_var.set("")
        self.claimant_dob_var.set("")
        self.claimant_gender_var.set("")
        self.relationship_var.set("")
        self.contact_var.set("")
        self.claimant_email_var.set("")
        self.claimant_phone_var.set("")
        self.claimant_address_var.set("")
        self.claimant_occupation_var.set("")
        self.claimant_marital_status_var.set("")
        self.claimant_alternate_contact_var.set("")
        self.claimant_relationship_proof_var.set("")
        self.claimant_notes_text.delete(1.0, tk.END)
        
        self.current_claimant = None
        
        # Clear treeview selection
        self.claimants_tree.selection_remove(self.claimants_tree.selection())
