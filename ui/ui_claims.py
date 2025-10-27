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

# Import database models (will be implemented)
# from db.models_claims import ClaimsModel
# from db.models_claimants import ClaimantsModel
# from db.models_assets import AssetsModel


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
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize the claims processing window.
        
        Args:
            parent: Parent Tkinter window
        """
        self.parent = parent
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
        
        # Initialize database models (placeholder)
        # self.claims_model = ClaimsModel()
        # self.claimants_model = ClaimantsModel()
        # self.assets_model = AssetsModel()
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Create and layout the user interface components."""
        # Create notebook for tabs
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
        """Setup the claims management tab."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Claim form
        form_frame = ttk.LabelFrame(main_frame, text="Claim Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Form fields
        self._create_claim_form_fields(form_frame)
        
        # Right panel - Claims list
        list_frame = ttk.LabelFrame(main_frame, text="Claims List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Search and filter
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.claims_search_var = tk.StringVar()
        self.claims_search_var.trace('w', self._on_claims_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.claims_search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Status filter
        ttk.Label(search_frame, text="Status:").grid(row=0, column=2, padx=(10, 5))
        self.status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var, width=15, state="readonly")
        status_combo['values'] = ('All', 'Pending', 'Verified', 'Settled')
        status_combo.set('All')
        status_combo.bind('<<ComboboxSelected>>', self._on_status_filter_change)
        status_combo.grid(row=0, column=3)
        
        # Claims treeview
        self._create_claims_treeview(list_frame)
        
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
        
        # Form fields
        self._create_claimant_form_fields(form_frame)
        
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
    
    def _create_claim_form_fields(self, parent: ttk.Frame):
        """Create form input fields for claim data."""
        # Asset Selection
        ttk.Label(parent, text="Asset:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.asset_var = tk.StringVar()
        self.asset_combo = ttk.Combobox(parent, textvariable=self.asset_var, width=25, state="readonly")
        self.asset_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Claimant Selection
        ttk.Label(parent, text="Claimant:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.claimant_var = tk.StringVar()
        self.claimant_combo = ttk.Combobox(parent, textvariable=self.claimant_var, width=25, state="readonly")
        self.claimant_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Status
        ttk.Label(parent, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(parent, textvariable=self.status_var, width=25, state="readonly")
        status_combo['values'] = ('Pending', 'Verified', 'Settled')
        status_combo.set('Pending')
        status_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Notes
        ttk.Label(parent, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.notes_text = tk.Text(parent, width=25, height=4)
        self.notes_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_claimant_form_fields(self, parent: ttk.Frame):
        """Create form input fields for claimant data."""
        # National ID
        ttk.Label(parent, text="National ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.claimant_national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(parent, textvariable=self.claimant_national_id_var, width=25)
        national_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # First Name
        ttk.Label(parent, text="First Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.claimant_first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(parent, textvariable=self.claimant_first_name_var, width=25)
        first_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Last Name
        ttk.Label(parent, text="Last Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.claimant_last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(parent, textvariable=self.claimant_last_name_var, width=25)
        last_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Relationship
        ttk.Label(parent, text="Relationship:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.relationship_var = tk.StringVar()
        relationship_combo = ttk.Combobox(parent, textvariable=self.relationship_var, width=25)
        relationship_combo['values'] = ('Spouse', 'Child', 'Parent', 'Sibling', 'Other Relative', 'Executor', 'Other')
        relationship_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Contact
        ttk.Label(parent, text="Contact:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(parent, textvariable=self.contact_var, width=25)
        contact_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_claims_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying claims."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "Asset", "Claimant", "Status", "Filed Date", "Notes")
        self.claims_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "Asset": 200, "Claimant": 150, "Status": 80, "Filed Date": 100, "Notes": 150}
        for col in columns:
            self.claims_tree.heading(col, text=col)
            self.claims_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claims_tree.yview)
        self.claims_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.claims_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.claims_tree.bind("<<TreeviewSelect>>", self._on_claim_select)
    
    def _create_claimants_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying claimants."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "National ID", "First Name", "Last Name", "Relationship", "Contact")
        self.claimants_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "National ID": 100, "First Name": 120, "Last Name": 120, "Relationship": 100, "Contact": 150}
        for col in columns:
            self.claimants_tree.heading(col, text=col)
            self.claimants_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claimants_tree.yview)
        self.claimants_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.claimants_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.claimants_tree.bind("<<TreeviewSelect>>", self._on_claimant_select)
    
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
            # TODO: Replace with actual database call
            # self.claimants = self.claimants_model.get_all()
            
            # Placeholder data
            self.claimants = [
                {
                    "ClaimantId": 1,
                    "NationalId": "111222333",
                    "FirstName": "Mary",
                    "LastName": "Doe",
                    "Relationship": "Spouse",
                    "Contact": "mary.doe@email.com"
                },
                {
                    "ClaimantId": 2,
                    "NationalId": "444555666",
                    "FirstName": "Robert",
                    "LastName": "Smith",
                    "Relationship": "Child",
                    "Contact": "robert.smith@email.com"
                }
            ]
            
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
            # TODO: Replace with actual database call
            # self.assets = self.assets_model.get_all_with_details()
            
            # Placeholder data
            self.assets = [
                {
                    "AssetId": 1,
                    "AssetType": "Bank Account",
                    "Identifier": "ACC-123456",
                    "DeceasedName": "John Doe",
                    "InstitutionName": "National Bank"
                },
                {
                    "AssetId": 2,
                    "AssetType": "Insurance Policy",
                    "Identifier": "POL-789012",
                    "DeceasedName": "Jane Smith",
                    "InstitutionName": "State Insurance"
                }
            ]
            
            # Update combobox
            asset_names = [f"{a['AssetType']} - {a['Identifier']} ({a['DeceasedName']})" for a in self.assets]
            self.asset_combo['values'] = asset_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load assets: {e}")
    
    def _load_claims(self):
        """Load claims from database and populate the treeview."""
        try:
            # Clear existing items
            for item in self.claims_tree.get_children():
                self.claims_tree.delete(item)
            
            # TODO: Replace with actual database call
            # self.claims = self.claims_model.get_all_with_details()
            
            # Placeholder data
            self.claims = [
                {
                    "ClaimId": 1,
                    "AssetId": 1,
                    "ClaimantId": 1,
                    "Status": "Pending",
                    "FiledAt": "2024-01-15",
                    "Notes": "Initial claim submission",
                    "AssetName": "Bank Account - ACC-123456 (John Doe)",
                    "ClaimantName": "Mary Doe"
                },
                {
                    "ClaimId": 2,
                    "AssetId": 2,
                    "ClaimantId": 2,
                    "Status": "Verified",
                    "FiledAt": "2024-01-10",
                    "VerifiedAt": "2024-01-20",
                    "Notes": "Documents verified",
                    "AssetName": "Insurance Policy - POL-789012 (Jane Smith)",
                    "ClaimantName": "Robert Smith"
                }
            ]
            
            # Populate treeview
            self._refresh_claims_treeview()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load claims: {e}")
    
    def _refresh_claims_treeview(self):
        """Refresh the claims treeview with current data."""
        # Clear existing items
        for item in self.claims_tree.get_children():
            self.claims_tree.delete(item)
        
        # Filter by status if selected
        status_filter = self.status_filter_var.get()
        filtered_claims = self.claims
        if status_filter != 'All':
            filtered_claims = [c for c in self.claims if c['Status'] == status_filter]
        
        # Populate treeview
        for claim in filtered_claims:
            values = (
                claim["ClaimId"],
                claim["AssetName"],
                claim["ClaimantName"],
                claim["Status"],
                claim["FiledAt"],
                claim["Notes"][:50] + "..." if len(claim["Notes"]) > 50 else claim["Notes"]
            )
            self.claims_tree.insert("", tk.END, values=values)
    
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
    
    def _on_claim_select(self, event):
        """Handle claim selection in treeview."""
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
        # Set asset
        asset_name = claim.get("AssetName", "")
        self.asset_var.set(asset_name)
        
        # Set claimant
        claimant_name = claim.get("ClaimantName", "")
        self.claimant_var.set(claimant_name)
        
        # Set status
        self.status_var.set(claim.get("Status", ""))
        
        # Set notes
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(1.0, claim.get("Notes", ""))
    
    def _populate_claimant_form(self, claimant: Dict[str, Any]):
        """Populate claimant form fields with claimant data."""
        self.claimant_national_id_var.set(claimant.get("NationalId", ""))
        self.claimant_first_name_var.set(claimant.get("FirstName", ""))
        self.claimant_last_name_var.set(claimant.get("LastName", ""))
        self.relationship_var.set(claimant.get("Relationship", ""))
        self.contact_var.set(claimant.get("Contact", ""))
    
    def _on_claims_search_change(self, *args):
        """Handle search text change to filter claims."""
        search_text = self.claims_search_var.get().lower()
        
        # Clear treeview
        for item in self.claims_tree.get_children():
            self.claims_tree.delete(item)
        
        # Filter and display matching claims
        status_filter = self.status_filter_var.get()
        filtered_claims = self.claims
        if status_filter != 'All':
            filtered_claims = [c for c in self.claims if c['Status'] == status_filter]
        
        for claim in filtered_claims:
            if (search_text in claim["AssetName"].lower() or 
                search_text in claim["ClaimantName"].lower() or
                search_text in claim["Status"].lower() or
                search_text in claim["Notes"].lower()):
                
                values = (
                    claim["ClaimId"],
                    claim["AssetName"],
                    claim["ClaimantName"],
                    claim["Status"],
                    claim["FiledAt"],
                    claim["Notes"][:50] + "..." if len(claim["Notes"]) > 50 else claim["Notes"]
                )
                self.claims_tree.insert("", tk.END, values=values)
    
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
        self._refresh_claims_treeview()
    
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
            
            # TODO: Replace with actual database call
            # new_id = self.claims_model.create(claim_data)
            
            # Placeholder: simulate successful creation
            new_id = len(self.claims) + 1
            claim_data["ClaimId"] = new_id
            claim_data["FiledAt"] = datetime.date.today().strftime("%Y-%m-%d")
            claim_data["AssetName"] = self.asset_var.get()
            claim_data["ClaimantName"] = self.claimant_var.get()
            self.claims.append(claim_data)
            
            messagebox.showinfo("Success", "Claim added successfully.")
            self._clear_claim_form()
            self._load_claims()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add claim: {e}")
    
    def _add_claimant(self):
        """Add a new claimant record."""
        if not self._validate_claimant_form():
            return
        
        try:
            # Prepare claimant data
            claimant_data = {
                "NationalId": self.claimant_national_id_var.get().strip() or None,
                "FirstName": self.claimant_first_name_var.get().strip(),
                "LastName": self.claimant_last_name_var.get().strip(),
                "Relationship": self.relationship_var.get().strip() or None,
                "Contact": self.contact_var.get().strip() or None
            }
            
            # TODO: Replace with actual database call
            # new_id = self.claimants_model.create(claimant_data)
            
            # Placeholder: simulate successful creation
            new_id = len(self.claimants) + 1
            claimant_data["ClaimantId"] = new_id
            self.claimants.append(claimant_data)
            
            messagebox.showinfo("Success", "Claimant added successfully.")
            self._clear_claimant_form()
            self._load_claimants()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add claimant: {e}")
    
    def _update_claim_status(self):
        """Update the selected claim status."""
        if not self.current_claim:
            messagebox.showwarning("No Selection", "Please select a claim to update.")
            return
        
        try:
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
            
            # TODO: Replace with actual database call
            # self.claims_model.update(updated_data["ClaimId"], updated_data)
            
            # Placeholder: update local data
            for i, claim in enumerate(self.claims):
                if claim["ClaimId"] == updated_data["ClaimId"]:
                    self.claims[i].update(updated_data)
                    break
            
            messagebox.showinfo("Success", "Claim status updated successfully.")
            self._load_claims()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update claim: {e}")
    
    def _update_claimant(self):
        """Update the selected claimant record."""
        if not self.current_claimant:
            messagebox.showwarning("No Selection", "Please select a claimant to update.")
            return
        
        if not self._validate_claimant_form():
            return
        
        try:
            # Prepare updated data
            updated_data = {
                "ClaimantId": self.current_claimant["ClaimantId"],
                "NationalId": self.claimant_national_id_var.get().strip() or None,
                "FirstName": self.claimant_first_name_var.get().strip(),
                "LastName": self.claimant_last_name_var.get().strip(),
                "Relationship": self.relationship_var.get().strip() or None,
                "Contact": self.contact_var.get().strip() or None
            }
            
            # TODO: Replace with actual database call
            # self.claimants_model.update(updated_data["ClaimantId"], updated_data)
            
            # Placeholder: update local data
            for i, claimant in enumerate(self.claimants):
                if claimant["ClaimantId"] == updated_data["ClaimantId"]:
                    self.claimants[i] = updated_data
                    break
            
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
            # TODO: Replace with actual database call
            # self.claims_model.delete(self.current_claim["ClaimId"])
            
            # Placeholder: remove from local data
            self.claims = [c for c in self.claims if c["ClaimId"] != self.current_claim["ClaimId"]]
            
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
            # TODO: Replace with actual database call
            # self.claimants_model.delete(self.current_claimant["ClaimantId"])
            
            # Placeholder: remove from local data
            self.claimants = [c for c in self.claimants if c["ClaimantId"] != self.current_claimant["ClaimantId"]]
            
            messagebox.showinfo("Success", "Claimant deleted successfully.")
            self._clear_claimant_form()
            self._load_claimants()
            
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
        self.claims_tree.selection_remove(self.claims_tree.selection())
    
    def _clear_claimant_form(self):
        """Clear all claimant form fields."""
        self.claimant_national_id_var.set("")
        self.claimant_first_name_var.set("")
        self.claimant_last_name_var.set("")
        self.relationship_var.set("")
        self.contact_var.set("")
        self.current_claimant = None
        
        # Clear treeview selection
        self.claimants_tree.selection_remove(self.claimants_tree.selection())
