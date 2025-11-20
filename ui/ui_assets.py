"""
FARVS Asset Management Module
=============================

This module provides CRUD operations for managing assets linked to deceased persons
in the FARVS database through a Tkinter interface.

Structure:
- AssetsWindow: Main window class for asset management
- Asset form handling: Add, edit, delete assets with deceased person linkage
- Institution management: Link assets to financial institutions
- Data validation: Input validation and relationship integrity
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
import decimal

# Import database models
from db.models_assets import AssetsModel
from db.models_deceased import DeceasedModel
from db.models_institutions import InstitutionsModel
from db.models_audit import AuditLogModel
from auth.session import get_current_user
from ui.theme import stripe_treeview
from logging_config import get_logger

logger = get_logger(__name__)


class AssetsWindow:
    """
    Tkinter window for managing asset records linked to deceased persons.
    
    Features:
    - Add new assets linked to deceased persons
    - Edit existing asset records
    - Delete assets (with confirmation)
    - Institution management
    - Asset value tracking
    - Search and filter by deceased person
    """
    
    def __init__(self, parent: tk.Tk, container: Optional[ttk.Frame] = None):
        """
        Initialize the asset management window.
        
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
            self.window.title("Asset Management")
            self.window.geometry("1000x750")
            self.window.minsize(900, 650)
        
        # Data storage
        self.current_asset: Optional[Dict[str, Any]] = None
        self.assets: List[Dict[str, Any]] = []
        self.deceased_persons: List[Dict[str, Any]] = []
        self.institutions: List[Dict[str, Any]] = []
        
        # Initialize database models
        self.assets_model = AssetsModel()
        self.deceased_model = DeceasedModel()
        self.institutions_model = InstitutionsModel()
        self.audit = AuditLogModel()
        
        self._setup_ui()
        self._load_data()
    
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
        form_frame = ttk.LabelFrame(main_frame, text="Asset Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        
        # Form fields container - Use ScrollableFrame for scrolling support
        from ui.scrollable_frame import ScrollableFrame
        form_fields_container = ScrollableFrame(form_frame)
        form_fields_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Create form fields in the inner_frame of ScrollableFrame
        self._create_form_fields(form_fields_container.inner_frame)
        
        # Right panel - Assets list with view toggle
        list_frame = ttk.LabelFrame(main_frame, text="Assets List", padding="10")
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
        
        # Assets display container - CRITICAL: Must have proper grid weights
        self.assets_container = ttk.Frame(list_frame)
        self.assets_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.assets_container.columnconfigure(0, weight=1)
        self.assets_container.rowconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Assets treeview (default)
        self._create_assets_treeview(self.assets_container)
        
        # Card view (hidden by default)
        self.card_view_frame = None
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_action_buttons(actions_frame)
    
    def _create_form_fields(self, parent: ttk.Frame):
        """Create form input fields for asset data."""
        # Deceased Person Selection
        ttk.Label(parent, text="Deceased Person:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.deceased_var = tk.StringVar()
        self.deceased_combo = ttk.Combobox(parent, textvariable=self.deceased_var, width=22, state="readonly")
        self.deceased_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Institution Selection
        ttk.Label(parent, text="Institution:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.institution_var = tk.StringVar()
        self.institution_combo = ttk.Combobox(parent, textvariable=self.institution_var, width=22, state="readonly")
        self.institution_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Asset Type
        ttk.Label(parent, text="Asset Type:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.asset_type_var = tk.StringVar()
        asset_type_combo = ttk.Combobox(parent, textvariable=self.asset_type_var, width=22, state="readonly")
        asset_type_combo['values'] = ('Bank Account', 'Investment', 'Insurance Policy', 'Real Estate', 'Vehicle', 'Other')
        asset_type_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        asset_type_combo.bind('<<ComboboxSelected>>', self._on_asset_type_change)
        
        # Store reference to form parent for dynamic fields
        self.form_parent = parent
        self.dynamic_fields = {}  # Store dynamic field widgets
        
        # Initialize field variables BEFORE creating dynamic container
        self._initialize_field_variables()
        
        # Asset Identifier
        ttk.Label(parent, text="Account/Policy ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.identifier_var = tk.StringVar()
        identifier_entry = ttk.Entry(parent, textvariable=self.identifier_var, width=25)
        identifier_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Estimated Value
        ttk.Label(parent, text="Estimated Value:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(parent, textvariable=self.value_var, width=25)
        value_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Label(parent, text="(USD)", font=("Arial", 8)).grid(row=4, column=2, sticky=tk.W, padx=(5, 0))
        
        # Additional Information Section - Dynamic fields container
        section_label = ttk.Label(parent, text="Additional Information", font=("Segoe UI", 10, "bold"))
        section_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Container for dynamic fields (will be populated based on asset type)
        self.dynamic_fields_container = ttk.Frame(parent)
        self.dynamic_fields_container.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        parent.columnconfigure(1, weight=1)
        
        # Common fields that are always visible (Documentation and Notes)
        # Documentation
        ttk.Label(parent, text="Documentation:").grid(row=20, column=0, sticky=tk.W, pady=2)
        self.documentation_var = tk.StringVar()
        documentation_entry = ttk.Entry(parent, textvariable=self.documentation_var, width=25)
        documentation_entry.grid(row=20, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Notes
        ttk.Label(parent, text="Notes:").grid(row=21, column=0, sticky=tk.W, pady=2)
        self.notes_text = tk.Text(parent, width=25, height=3)
        self.notes_text.grid(row=21, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
        
        # Trigger initial update if asset type is already set
        if self.asset_type_var.get():
            self._update_dynamic_fields(self.asset_type_var.get())
    
    def _create_assets_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying assets."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Treeview columns
        columns = ("ID", "Deceased", "Type", "Institution", "Identifier", "Value")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "Deceased": 150, "Type": 120, "Institution": 150, "Identifier": 120, "Value": 100}
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
        self.tree.bind("<<TreeviewSelect>>", self._on_asset_select)
    
    def _create_action_buttons(self, parent: ttk.Frame):
        """Create action buttons for CRUD operations."""
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        ttk.Button(btn_frame, text="Add Asset", command=self._add_asset, width=12).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Update", command=self._update_asset, width=12).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._delete_asset, width=12).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self._clear_form, width=12).grid(row=0, column=3, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_data, width=12).grid(row=0, column=4, padx=2)
    
    def _load_data(self):
        """Load all required data from database."""
        try:
            logger.debug("Loading data from database...")
            # Load deceased persons
            self._load_deceased_persons()
            logger.info(f"Loaded {len(self.deceased_persons)} deceased persons")
            
            # Load institutions
            self._load_institutions()
            logger.info(f"Loaded {len(self.institutions)} institutions")
            
            # Load assets
            self._load_assets()
            logger.info(f"Loaded {len(self.assets)} assets")
            
        except Exception as e:
            error_msg = f"Failed to load data: {e}"
            logger.error(f"Error in _load_data: {error_msg}", exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _load_deceased_persons(self):
        """Load deceased persons for the dropdown."""
        try:
            # Load deceased persons from database
            self.deceased_persons = self.deceased_model.get_all()
            
            # Update combobox with deceased person names
            deceased_names = [f"{p['FirstName']} {p['LastName']}" for p in self.deceased_persons]
            self.deceased_combo['values'] = deceased_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deceased persons: {e}")
    
    def _load_institutions(self):
        """Load institutions for the dropdown."""
        try:
            # Load institutions from database
            self.institutions = self.institutions_model.get_all()
            
            # Update combobox with institution names
            institution_names = [f"{i['Name']} ({i['Type']})" for i in self.institutions]
            self.institution_combo['values'] = institution_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load institutions: {e}")
    
    def _load_assets(self):
        """Load assets from database and populate the display."""
        try:
            # Load assets from database with detailed information
            self.assets = self.assets_model.get_all_with_details()
            logger.info(f"Loaded {len(self.assets)} assets from database")
            
            # Ensure assets_container exists
            if not hasattr(self, 'assets_container'):
                logger.warning("assets_container not initialized yet")
                return
            
            # Show empty state if no assets
            if not self.assets:
                from ui.components import EmptyState
                for widget in self.assets_container.winfo_children():
                    widget.destroy()
                EmptyState.show(
                    self.assets_container,
                    "No assets found",
                    "Add New Asset",
                    self._add_asset
                )
                return
            
            # Update display based on view mode
            self._update_display()
                
        except Exception as e:
            error_msg = f"Failed to load assets: {e}"
            logger.error(f"Error in _load_assets: {error_msg}", exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _toggle_view(self):
        """Toggle between table and card view."""
        self._update_display()
    
    def _update_display(self):
        """Update display based on current view mode."""
        # Clear container
        for widget in self.assets_container.winfo_children():
            widget.destroy()
        
        if self.view_mode.get() == "cards":
            self._display_cards()
        else:
            self._display_table()
    
    def _display_table(self):
        """Display assets in table view."""
        # Always recreate treeview to ensure it's in the right container
        self._create_assets_treeview(self.assets_container)
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate treeview
        for asset in self.assets:
            values = (
                asset["AssetId"],
                asset["DeceasedName"],
                asset["AssetType"],
                asset["InstitutionName"],
                asset["Identifier"],
                f"${asset['EstimatedValue']:,.2f}"
            )
            self.tree.insert("", tk.END, values=values)
        stripe_treeview(self.tree)
    
    def _display_cards(self):
        """Display assets in card view."""
        from ui.record_display import RecordGridView
        
        # Create card view frame (recreate each time to avoid conflicts)
        self.card_view_frame = ttk.Frame(self.assets_container)
        self.card_view_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.assets_container.columnconfigure(0, weight=1)
        self.assets_container.rowconfigure(0, weight=1)
        self.card_view_frame.columnconfigure(0, weight=1)
        self.card_view_frame.rowconfigure(0, weight=1)
        
        # Create grid view
        grid_view = RecordGridView(
            self.card_view_frame,
            card_type="asset",
            columns=3,
            on_select=self._on_card_select
        )
        grid_view.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Display records
        grid_view.display_records(self.assets)
        self.current_grid_view = grid_view
    
    def _on_card_select(self, record: Dict[str, Any]):
        """Handle card selection."""
        self.current_asset = record
        self._populate_form(record)
    
    def _on_asset_select(self, event):
        """Handle asset selection in treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected asset data
        item = self.tree.item(selection[0])
        asset_id = item['values'][0]
        
        # Find asset in data
        self.current_asset = next((a for a in self.assets if a["AssetId"] == asset_id), None)
        
        if self.current_asset:
            self._populate_form(self.current_asset)
    
    def _populate_form(self, asset: Dict[str, Any]):
        """Populate form fields with asset data."""
        # Set deceased person
        deceased_name = asset.get("DeceasedName", "")
        self.deceased_var.set(deceased_name)
        
        # Set institution
        institution_name = asset.get("InstitutionName", "")
        self.institution_var.set(institution_name)
        
        # Set other fields
        self.asset_type_var.set(asset.get("AssetType", ""))
        self.identifier_var.set(asset.get("Identifier", ""))
        self.value_var.set(str(asset.get("EstimatedValue", "")))
        
        # Populate all new fields
        self.account_status_var.set(asset.get('AccountStatus', '') or '')
        self.currency_var.set(asset.get('Currency', 'USD') or 'USD')
        account_opening = asset.get('AccountOpeningDate', '')
        if account_opening:
            self.account_opening_picker.value.set(str(account_opening)[:10] if len(str(account_opening)) > 10 else str(account_opening))
        else:
            self.account_opening_picker.value.set("")
        last_transaction = asset.get('LastTransactionDate', '')
        if last_transaction:
            self.last_transaction_picker.value.set(str(last_transaction)[:10] if len(str(last_transaction)) > 10 else str(last_transaction))
        else:
            self.last_transaction_picker.value.set("")
        self.interest_rate_var.set(str(asset.get('InterestRate', '')) if asset.get('InterestRate') else '')
        maturity = asset.get('MaturityDate', '')
        if maturity:
            self.maturity_picker.value.set(str(maturity)[:10] if len(str(maturity)) > 10 else str(maturity))
        else:
            self.maturity_picker.value.set("")
        self.beneficiary_var.set(asset.get('BeneficiaryInfo', '') or '')
        self.account_holder_var.set(asset.get('AccountHolderName', '') or '')
        self.branch_var.set(asset.get('BranchLocation', '') or '')
        self.documentation_var.set(asset.get('Documentation', '') or '')
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(1.0, asset.get('Notes', '') or '')
    
    def _on_search_change(self, *args):
        """Handle search text change to filter assets."""
        search_text = self.search_var.get().lower()
        
        # Filter assets
        filtered_assets = [
            a for a in self.assets
            if (search_text in a["DeceasedName"].lower() or 
                search_text in a["AssetType"].lower() or
                search_text in a["InstitutionName"].lower() or
                (a["Identifier"] and search_text in a["Identifier"].lower()))
        ]
        
        # Update display with filtered assets
        if self.view_mode.get() == "cards":
            if hasattr(self, 'current_grid_view'):
                self.current_grid_view.display_records(filtered_assets)
        else:
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Populate with filtered assets
            for asset in filtered_assets:
                values = (
                    asset["AssetId"],
                    asset["DeceasedName"],
                    asset["AssetType"],
                    asset["InstitutionName"],
                    asset["Identifier"],
                    f"${asset['EstimatedValue']:,.2f}"
                )
                self.tree.insert("", tk.END, values=values)
            stripe_treeview(self.tree)
    
    def _validate_form(self) -> bool:
        """Validate form input data."""
        # Required fields
        if not self.deceased_var.get().strip():
            messagebox.showerror("Validation Error", "Please select a deceased person.")
            return False
        
        if not self.institution_var.get().strip():
            messagebox.showerror("Validation Error", "Please select an institution.")
            return False
        
        if not self.asset_type_var.get().strip():
            messagebox.showerror("Validation Error", "Asset type is required.")
            return False
        
        # Value validation
        value_text = self.value_var.get().strip()
        if value_text:
            try:
                float(value_text)
                if float(value_text) < 0:
                    messagebox.showerror("Validation Error", "Value cannot be negative.")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Value must be a valid number.")
                return False
        
        return True
    
    def _get_selected_deceased_id(self) -> Optional[int]:
        """Get the selected deceased person ID."""
        deceased_name = self.deceased_var.get()
        if not deceased_name:
            return None
        
        for person in self.deceased_persons:
            if f"{person['FirstName']} {person['LastName']}" == deceased_name:
                return person["DeceasedId"]
        return None
    
    def _get_selected_institution_id(self) -> Optional[int]:
        """Get the selected institution ID."""
        institution_name = self.institution_var.get()
        if not institution_name:
            return None
        
        for institution in self.institutions:
            if f"{institution['Name']} ({institution['Type']})" == institution_name:
                return institution["InstitutionId"]
        return None
    
    def _add_asset(self):
        """Add a new asset using modal."""
        from ui.modals import AddAssetModal
        
        def on_save(asset_data):
            """Handle save from modal."""
            try:
                # DB create
                new_id = self.assets_model.create(asset_data)
                # Audit
                user = get_current_user()
                self.audit.write(
                    user_id=user["UserId"] if user else None,
                    action="CREATE",
                    entity="Asset",
                    entity_id=str(new_id),
                    details=f"Created asset {asset_data['AssetType']}",
                    ip=None
                )
            
                messagebox.showinfo("Success", "Asset added successfully.")
                self._load_assets()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add asset: {e}")
        
        # Show modal
        modal = AddAssetModal(self.window, self.deceased_persons, self.institutions, on_save)
        modal.show()
    
    def _update_asset(self):
        """Update the selected asset record."""
        if not self.current_asset:
            messagebox.showwarning("No Selection", "Please select an asset to update.")
            return
        
        if not self._validate_form():
            return
        
        try:
            # Get selected IDs
            deceased_id = self._get_selected_deceased_id()
            institution_id = self._get_selected_institution_id()
            
            if not deceased_id or not institution_id:
                messagebox.showerror("Error", "Invalid selection for deceased person or institution.")
                return
            
            # Get date values from date pickers
            account_opening = self.account_opening_picker.get() if hasattr(self, 'account_opening_picker') else None
            last_transaction = self.last_transaction_picker.get() if hasattr(self, 'last_transaction_picker') else None
            maturity = self.maturity_picker.get() if hasattr(self, 'maturity_picker') else None
            notes = self.notes_text.get(1.0, tk.END).strip()
            interest_rate = self.interest_rate_var.get().strip()
            
            # Prepare updated data
            updated_data = {
                "AssetId": self.current_asset["AssetId"],
                "DeceasedId": deceased_id,
                "InstitutionId": institution_id,
                "AssetType": self.asset_type_var.get().strip(),
                "Identifier": self.identifier_var.get().strip() or None,
                "EstimatedValue": float(self.value_var.get()) if self.value_var.get().strip() else None,
                "AccountStatus": self.account_status_var.get().strip() or None,
                "AccountOpeningDate": account_opening if account_opening and account_opening != "YYYY-MM-DD" else None,
                "LastTransactionDate": last_transaction if last_transaction and last_transaction != "YYYY-MM-DD" else None,
                "InterestRate": float(interest_rate) if interest_rate else None,
                "MaturityDate": maturity if maturity and maturity != "YYYY-MM-DD" else None,
                "BeneficiaryInfo": self.beneficiary_var.get().strip() or None,
                "AccountHolderName": self.account_holder_var.get().strip() or None,
                "BranchLocation": self.branch_var.get().strip() or None,
                "Currency": self.currency_var.get().strip() or "USD",
                "Documentation": self.documentation_var.get().strip() or None,
                "Notes": notes if notes else None
            }
            
            # Update asset in database
            success = self.assets_model.update(updated_data["AssetId"], updated_data)
            
            if success:
                # Log audit entry
                user = get_current_user()
                if user:
                    self.audit.write(
                        user_id=user.get('UserId'),
                        action='UPDATE',
                        entity='Asset',
                        entity_id=str(updated_data["AssetId"]),
                        details=f"Updated asset: {updated_data['AssetType']}",
                        ip=None
                    )
            
                messagebox.showinfo("Success", "Asset updated successfully.")
                self._load_assets()
            else:
                messagebox.showerror("Error", "Failed to update asset. Asset may not exist.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update asset: {e}")
    
    def _delete_asset(self):
        """Delete the selected asset record."""
        if not self.current_asset:
            messagebox.showwarning("No Selection", "Please select an asset to delete.")
            return
        
        # Confirmation dialog
        asset_info = f"{self.current_asset['AssetType']} - {self.current_asset['Identifier']}"
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the asset: {asset_info}?"):
            return
        
        try:
            # Delete asset from database
            asset_id = self.current_asset["AssetId"]
            success = self.assets_model.delete(asset_id)
            
            if success:
                # Log audit entry
                user = get_current_user()
                if user:
                    self.audit.write(
                        user_id=user.get('UserId'),
                        action='DELETE',
                        entity='Asset',
                        entity_id=str(asset_id),
                        details=f"Deleted asset: {self.current_asset['AssetType']}",
                        ip=None
                    )
            
                messagebox.showinfo("Success", "Asset deleted successfully.")
                self._clear_form()
                self._load_assets()
            else:
                messagebox.showerror("Error", "Failed to delete asset. Asset may not exist.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete asset: {e}")
    
    def _clear_form(self):
        """Clear all form fields."""
        self.deceased_var.set("")
        self.institution_var.set("")
        self.asset_type_var.set("")
        self.identifier_var.set("")
        self.value_var.set("")
        self.account_status_var.set("")
        self.currency_var.set("USD")
        self.account_opening_picker.value.set("")
        self.last_transaction_picker.value.set("")
        self.interest_rate_var.set("")
        self.maturity_picker.value.set("")
        self.beneficiary_var.set("")
        self.account_holder_var.set("")
        self.branch_var.set("")
        self.documentation_var.set("")
        self.notes_text.delete(1.0, tk.END)
        
        self.current_asset = None
        
        # Clear dynamic fields
        if hasattr(self, 'asset_type_var'):
            self._update_dynamic_fields(self.asset_type_var.get() if self.asset_type_var.get() else "")
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
    
    def _initialize_field_variables(self):
        """Initialize all possible field variables."""
        # Bank Account fields
        self.account_status_var = tk.StringVar()
        self.currency_var = tk.StringVar(value="USD")
        self.interest_rate_var = tk.StringVar()
        self.beneficiary_var = tk.StringVar()
        self.account_holder_var = tk.StringVar()
        self.branch_var = tk.StringVar()
        
        # Vehicle fields
        self.vehicle_make_var = tk.StringVar()
        self.vehicle_model_var = tk.StringVar()
        self.vehicle_year_var = tk.StringVar()
        self.vehicle_vin_var = tk.StringVar()
        self.vehicle_registration_var = tk.StringVar()
        self.vehicle_condition_var = tk.StringVar()
        self.vehicle_mileage_var = tk.StringVar()
        
        # Real Estate fields
        self.property_address_var = tk.StringVar()
        self.property_type_var = tk.StringVar()
        self.property_size_var = tk.StringVar()
        self.property_condition_var = tk.StringVar()
        self.property_tax_id_var = tk.StringVar()
        
        # Insurance Policy fields
        self.policy_number_var = tk.StringVar()
        self.policy_type_var = tk.StringVar()
        self.premium_amount_var = tk.StringVar()
        
        # Other fields
        self.description_var = tk.StringVar()
    
    def _on_asset_type_change(self, event=None):
        """Handle asset type change to show/hide relevant fields."""
        asset_type = self.asset_type_var.get()
        print(f"Asset type changed to: {asset_type}")  # Debug
        self._update_dynamic_fields(asset_type)
    
    def _update_dynamic_fields(self, asset_type: str):
        """Update dynamic fields based on asset type."""
        # Ensure container exists
        if not hasattr(self, 'dynamic_fields_container') or not self.dynamic_fields_container:
            print("Dynamic fields container not found!")  # Debug
            return
        
        print(f"Updating dynamic fields for: {asset_type}")  # Debug
            
        # Clear existing dynamic fields
        for widget in self.dynamic_fields_container.winfo_children():
            widget.destroy()
        if hasattr(self, 'dynamic_fields'):
            self.dynamic_fields.clear()
        else:
            self.dynamic_fields = {}
        
        if not asset_type:
            print("No asset type selected")  # Debug
            return
        
        try:
            from ui.asset_form_fields import AssetFormFields
            from ui.components import DatePicker, create_tooltip
            
            fields = AssetFormFields.get_fields_for_type(asset_type)
            row = 0
            
            for field_id, label, field_type, options in fields:
                # Handle datepicker separately (it creates its own label)
                if field_type == 'datepicker':
                    picker = DatePicker(self.dynamic_fields_container, f"{label}:", required=False)
                    picker.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
                    setattr(self, f"{field_id}_picker", picker)
                    self.dynamic_fields[field_id] = picker
                    row += 1
                    continue
                
                # Label for other field types
                ttk.Label(self.dynamic_fields_container, text=f"{label}:").grid(
                    row=row, column=0, sticky=tk.W, pady=2
                )
                
                # Field widget
                if field_type == 'entry':
                    var = getattr(self, f"{field_id}_var", None)
                    if var is None:
                        var = tk.StringVar()
                        setattr(self, f"{field_id}_var", var)
                    entry = ttk.Entry(self.dynamic_fields_container, textvariable=var, width=25)
                    entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
                    self.dynamic_fields[field_id] = entry
                    create_tooltip(entry, f"Optional: {label}")
                    
                elif field_type == 'combobox':
                    var = getattr(self, f"{field_id}_var", None)
                    if var is None:
                        var = tk.StringVar()
                        setattr(self, f"{field_id}_var", var)
                    combo = ttk.Combobox(self.dynamic_fields_container, textvariable=var, width=22)
                    if options:
                        combo['values'] = options
                    combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
                    self.dynamic_fields[field_id] = combo
                    create_tooltip(combo, f"Optional: {label}")
                    
                elif field_type == 'text':
                    var = getattr(self, f"{field_id}_var", None)
                    if var is None:
                        var = tk.StringVar()
                        setattr(self, f"{field_id}_var", var)
                    text_widget = tk.Text(self.dynamic_fields_container, width=25, height=3)
                    text_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
                    self.dynamic_fields[field_id] = text_widget
                    create_tooltip(text_widget, f"Optional: {label}")
                
                row += 1
            
            # Configure column weights
            self.dynamic_fields_container.columnconfigure(1, weight=1)
        except Exception as e:
            logger.error(f"Error updating dynamic fields: {e}", exc_info=True)
