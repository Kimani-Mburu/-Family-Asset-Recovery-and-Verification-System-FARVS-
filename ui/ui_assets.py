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

# Import database models (will be implemented)
# from db.models_assets import AssetsModel
# from db.models_deceased import DeceasedModel
# from db.models_institutions import InstitutionsModel


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
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize the asset management window.
        
        Args:
            parent: Parent Tkinter window
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Asset Management")
        self.window.geometry("1000x750")
        self.window.minsize(900, 650)
        
        # Data storage
        self.current_asset: Optional[Dict[str, Any]] = None
        self.assets: List[Dict[str, Any]] = []
        self.deceased_persons: List[Dict[str, Any]] = []
        self.institutions: List[Dict[str, Any]] = []
        
        # Initialize database models (placeholder)
        # self.assets_model = AssetsModel()
        # self.deceased_model = DeceasedModel()
        # self.institutions_model = InstitutionsModel()
        
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
        
        # Form fields
        self._create_form_fields(form_frame)
        
        # Right panel - Assets list
        list_frame = ttk.LabelFrame(main_frame, text="Assets List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Search and filter
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Assets treeview
        self._create_assets_treeview(list_frame)
        
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
        asset_type_combo = ttk.Combobox(parent, textvariable=self.asset_type_var, width=22)
        asset_type_combo['values'] = ('Bank Account', 'Investment', 'Insurance Policy', 'Real Estate', 'Vehicle', 'Other')
        asset_type_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
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
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_assets_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying assets."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "Deceased", "Type", "Institution", "Identifier", "Value")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "Deceased": 150, "Type": 120, "Institution": 150, "Identifier": 120, "Value": 100}
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
            # Load deceased persons
            self._load_deceased_persons()
            
            # Load institutions
            self._load_institutions()
            
            # Load assets
            self._load_assets()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def _load_deceased_persons(self):
        """Load deceased persons for the dropdown."""
        try:
            # TODO: Replace with actual database call
            # self.deceased_persons = self.deceased_model.get_all()
            
            # Placeholder data
            self.deceased_persons = [
                {"DeceasedId": 1, "FirstName": "John", "LastName": "Doe"},
                {"DeceasedId": 2, "FirstName": "Jane", "LastName": "Smith"}
            ]
            
            # Update combobox
            deceased_names = [f"{p['FirstName']} {p['LastName']}" for p in self.deceased_persons]
            self.deceased_combo['values'] = deceased_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load deceased persons: {e}")
    
    def _load_institutions(self):
        """Load institutions for the dropdown."""
        try:
            # TODO: Replace with actual database call
            # self.institutions = self.institutions_model.get_all()
            
            # Placeholder data
            self.institutions = [
                {"InstitutionId": 1, "Name": "National Bank", "Type": "Bank"},
                {"InstitutionId": 2, "Name": "State Insurance", "Type": "Insurance"}
            ]
            
            # Update combobox
            institution_names = [f"{i['Name']} ({i['Type']})" for i in self.institutions]
            self.institution_combo['values'] = institution_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load institutions: {e}")
    
    def _load_assets(self):
        """Load assets from database and populate the treeview."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # TODO: Replace with actual database call
            # self.assets = self.assets_model.get_all_with_details()
            
            # Placeholder data
            self.assets = [
                {
                    "AssetId": 1,
                    "DeceasedId": 1,
                    "InstitutionId": 1,
                    "AssetType": "Bank Account",
                    "Identifier": "ACC-123456",
                    "EstimatedValue": 50000.00,
                    "DeceasedName": "John Doe",
                    "InstitutionName": "National Bank"
                },
                {
                    "AssetId": 2,
                    "DeceasedId": 2,
                    "InstitutionId": 2,
                    "AssetType": "Insurance Policy",
                    "Identifier": "POL-789012",
                    "EstimatedValue": 100000.00,
                    "DeceasedName": "Jane Smith",
                    "InstitutionName": "State Insurance"
                }
            ]
            
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
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load assets: {e}")
    
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
    
    def _on_search_change(self, *args):
        """Handle search text change to filter assets."""
        search_text = self.search_var.get().lower()
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and display matching assets
        for asset in self.assets:
            if (search_text in asset["DeceasedName"].lower() or 
                search_text in asset["AssetType"].lower() or
                search_text in asset["InstitutionName"].lower() or
                search_text in asset["Identifier"].lower()):
                
                values = (
                    asset["AssetId"],
                    asset["DeceasedName"],
                    asset["AssetType"],
                    asset["InstitutionName"],
                    asset["Identifier"],
                    f"${asset['EstimatedValue']:,.2f}"
                )
                self.tree.insert("", tk.END, values=values)
    
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
        """Add a new asset record."""
        if not self._validate_form():
            return
        
        try:
            # Get selected IDs
            deceased_id = self._get_selected_deceased_id()
            institution_id = self._get_selected_institution_id()
            
            if not deceased_id or not institution_id:
                messagebox.showerror("Error", "Invalid selection for deceased person or institution.")
                return
            
            # Prepare asset data
            asset_data = {
                "DeceasedId": deceased_id,
                "InstitutionId": institution_id,
                "AssetType": self.asset_type_var.get().strip(),
                "Identifier": self.identifier_var.get().strip() or None,
                "EstimatedValue": float(self.value_var.get()) if self.value_var.get().strip() else None
            }
            
            # TODO: Replace with actual database call
            # new_id = self.assets_model.create(asset_data)
            
            # Placeholder: simulate successful creation
            new_id = len(self.assets) + 1
            asset_data["AssetId"] = new_id
            asset_data["DeceasedName"] = self.deceased_var.get()
            asset_data["InstitutionName"] = self.institution_var.get()
            self.assets.append(asset_data)
            
            messagebox.showinfo("Success", "Asset added successfully.")
            self._clear_form()
            self._load_assets()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add asset: {e}")
    
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
            
            # Prepare updated data
            updated_data = {
                "AssetId": self.current_asset["AssetId"],
                "DeceasedId": deceased_id,
                "InstitutionId": institution_id,
                "AssetType": self.asset_type_var.get().strip(),
                "Identifier": self.identifier_var.get().strip() or None,
                "EstimatedValue": float(self.value_var.get()) if self.value_var.get().strip() else None
            }
            
            # TODO: Replace with actual database call
            # self.assets_model.update(updated_data["AssetId"], updated_data)
            
            # Placeholder: update local data
            for i, asset in enumerate(self.assets):
                if asset["AssetId"] == updated_data["AssetId"]:
                    updated_data["DeceasedName"] = self.deceased_var.get()
                    updated_data["InstitutionName"] = self.institution_var.get()
                    self.assets[i] = updated_data
                    break
            
            messagebox.showinfo("Success", "Asset updated successfully.")
            self._load_assets()
            
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
            # TODO: Replace with actual database call
            # self.assets_model.delete(self.current_asset["AssetId"])
            
            # Placeholder: remove from local data
            self.assets = [a for a in self.assets if a["AssetId"] != self.current_asset["AssetId"]]
            
            messagebox.showinfo("Success", "Asset deleted successfully.")
            self._clear_form()
            self._load_assets()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete asset: {e}")
    
    def _clear_form(self):
        """Clear all form fields."""
        self.deceased_var.set("")
        self.institution_var.set("")
        self.asset_type_var.set("")
        self.identifier_var.set("")
        self.value_var.set("")
        self.current_asset = None
        
        # Clear treeview selection
        self.tree.selection_remove(self.tree.selection())
