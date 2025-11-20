"""
Modal Forms for Adding New Records in FARVS

This module provides modal dialogs for adding new records (deceased, assets, claimants).
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from ui.components import ModalDialog, DatePicker, create_tooltip


class AddDeceasedModal:
    """Modal for adding a new deceased record."""
    
    def __init__(self, parent: tk.Tk, on_save: Callable[[Dict[str, Any]], None]):
        """
        Initialize the modal.
        
        Args:
            parent: Parent window
            on_save: Callback function that receives the record data
        """
        self.on_save = on_save
        self.modal = ModalDialog(parent, "Add New Deceased Record", width=500, height=450)
        
        # Form fields
        form_frame = ttk.Frame(self.modal.content_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # National ID
        ttk.Label(form_frame, text="National ID:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(form_frame, textvariable=self.national_id_var, width=30, font=("Segoe UI", 10))
        national_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        create_tooltip(national_id_entry, "Optional: National identification number")
        
        # First Name (Required)
        label_frame = ttk.Frame(form_frame)
        label_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="First Name:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(2, 0))
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(form_frame, textvariable=self.first_name_var, width=30, font=("Segoe UI", 10))
        first_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        first_name_entry.focus()
        create_tooltip(first_name_entry, "Required: First name of the deceased person")
        
        # Last Name (Required)
        label_frame = ttk.Frame(form_frame)
        label_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Last Name:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(2, 0))
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(form_frame, textvariable=self.last_name_var, width=30, font=("Segoe UI", 10))
        last_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        create_tooltip(last_name_entry, "Required: Last name of the deceased person")
        
        # Date of Birth
        self.dob_picker = DatePicker(form_frame, "Date of Birth:", required=False)
        self.dob_picker.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5, padx=(0, 10))
        
        # Date of Death
        self.dod_picker = DatePicker(form_frame, "Date of Death:", required=False)
        self.dod_picker.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5, padx=(0, 10))
        
        # Error label
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key
        first_name_entry.bind('<Return>', lambda e: last_name_entry.focus())
        last_name_entry.bind('<Return>', lambda e: self._save())
        
        # Buttons
        self.modal.add_button("Cancel", style="default")
        self.modal.add_button("Save", self._save, style="primary")
    
    def _save(self):
        """Save the record."""
        # Validate
        if not self.first_name_var.get().strip():
            self.error_label.config(text="First Name is required")
            return
        if not self.last_name_var.get().strip():
            self.error_label.config(text="Last Name is required")
            return
        
        # Get date values
        dob_value = self.dob_picker.get() if self.dob_picker.get() and self.dob_picker.get() != "YYYY-MM-DD" else None
        dod_value = self.dod_picker.get() if self.dod_picker.get() and self.dod_picker.get() != "YYYY-MM-DD" else None
        
        # Prepare record data
        record_data = {
            "NationalId": self.national_id_var.get().strip() or None,
            "FirstName": self.first_name_var.get().strip(),
            "LastName": self.last_name_var.get().strip(),
            "DateOfBirth": dob_value,
            "DateOfDeath": dod_value
        }
        
        # Call callback
        self.on_save(record_data)
        self.modal.dialog.destroy()
    
    def show(self):
        """Show the modal."""
        self.modal.show()


class AddAssetModal:
    """Modal for adding a new asset record with dynamic fields based on asset type."""
    
    def __init__(self, parent: tk.Tk, deceased_list: list, institutions_list: list, 
                 on_save: Callable[[Dict[str, Any]], None]):
        """
        Initialize the modal.
        
        Args:
            parent: Parent window
            deceased_list: List of deceased records
            institutions_list: List of institution records
            on_save: Callback function that receives the asset data
        """
        self.on_save = on_save
        self.deceased_list = deceased_list
        self.institutions_list = institutions_list
        self.modal = ModalDialog(parent, "Add New Asset", width=600, height=700)
        
        # Use ScrollableFrame for the form
        from ui.scrollable_frame import ScrollableFrame
        scrollable = ScrollableFrame(self.modal.content_frame)
        scrollable.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        form_frame = scrollable.inner_frame
        form_frame.configure(padding="20")
        
        row = 0
        
        # Basic Information Section
        section_label = ttk.Label(form_frame, text="Basic Information", font=("Segoe UI", 11, "bold"))
        section_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Deceased Person
        ttk.Label(form_frame, text="Deceased Person:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.deceased_var = tk.StringVar()
        deceased_names = [f"{d['FirstName']} {d['LastName']}" for d in deceased_list]
        self.deceased_combo = ttk.Combobox(form_frame, textvariable=self.deceased_var, width=27, state="readonly")
        self.deceased_combo['values'] = deceased_names
        self.deceased_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.deceased_combo.focus()
        row += 1
        
        # Institution
        ttk.Label(form_frame, text="Institution:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.institution_var = tk.StringVar()
        institution_names = [i['Name'] for i in institutions_list]
        self.institution_combo = ttk.Combobox(form_frame, textvariable=self.institution_var, width=27, state="readonly")
        self.institution_combo['values'] = institution_names
        self.institution_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # Asset Type
        ttk.Label(form_frame, text="Asset Type:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.asset_type_var = tk.StringVar()
        asset_type_combo = ttk.Combobox(form_frame, textvariable=self.asset_type_var, width=27, state="readonly")
        asset_type_combo['values'] = ('Bank Account', 'Investment', 'Insurance Policy', 'Real Estate', 'Vehicle', 'Other')
        asset_type_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        asset_type_combo.bind('<<ComboboxSelected>>', self._on_asset_type_change)
        row += 1
        
        # Identifier
        ttk.Label(form_frame, text="Account/Policy ID:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.identifier_var = tk.StringVar()
        identifier_entry = ttk.Entry(form_frame, textvariable=self.identifier_var, width=30, font=("Segoe UI", 10))
        identifier_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # Estimated Value
        ttk.Label(form_frame, text="Estimated Value:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(form_frame, textvariable=self.value_var, width=30, font=("Segoe UI", 10))
        value_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        ttk.Label(form_frame, text="(USD)", font=("Segoe UI", 8)).grid(row=row, column=2, sticky=tk.W, padx=(5, 0))
        row += 1
        
        # Additional Information Section - Dynamic fields container
        section_label2 = ttk.Label(form_frame, text="Additional Information", font=("Segoe UI", 11, "bold"))
        section_label2.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Container for dynamic fields
        self.dynamic_fields_container = ttk.Frame(form_frame)
        self.dynamic_fields_container.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.dynamic_fields = {}  # Store dynamic field widgets
        row += 1
        
        # Common fields
        # Documentation
        ttk.Label(form_frame, text="Documentation:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.documentation_var = tk.StringVar()
        documentation_entry = ttk.Entry(form_frame, textvariable=self.documentation_var, width=30, font=("Segoe UI", 10))
        documentation_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.notes_text = tk.Text(form_frame, width=30, height=3, font=("Segoe UI", 10))
        self.notes_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # Error label
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.grid(row=row, column=0, columnspan=2, pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Initialize field variables
        self._initialize_field_variables()
        
        # Buttons
        self.modal.add_button("Cancel", style="default")
        self.modal.add_button("Save", self._save, style="primary")
    
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
        
        # Investment fields
        self.investment_type_var = tk.StringVar()
        
        # Insurance Policy fields
        self.policy_number_var = tk.StringVar()
        self.policy_type_var = tk.StringVar()
        self.premium_amount_var = tk.StringVar()
    
    def _on_asset_type_change(self, event=None):
        """Handle asset type change to show/hide relevant fields."""
        asset_type = self.asset_type_var.get()
        self._update_dynamic_fields(asset_type)
    
    def _update_dynamic_fields(self, asset_type: str):
        """Update dynamic fields based on asset type."""
        # Clear existing dynamic fields
        for widget in self.dynamic_fields_container.winfo_children():
            widget.destroy()
        self.dynamic_fields.clear()
        
        if not asset_type:
            return
        
        try:
            from ui.asset_form_fields import AssetFormFields
            from ui.components import DatePicker, create_tooltip
            
            fields = AssetFormFields.get_fields_for_type(asset_type)
            row = 0
            
            for field_id, label, field_type, options in fields:
                # Handle datepicker separately
                if field_type == 'datepicker':
                    picker = DatePicker(self.dynamic_fields_container, f"{label}:", required=False)
                    picker.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
                    setattr(self, f"{field_id}_picker", picker)
                    self.dynamic_fields[field_id] = picker
                    row += 1
                    continue
                
                # Label for other field types
                ttk.Label(self.dynamic_fields_container, text=f"{label}:", font=("Segoe UI", 10)).grid(
                    row=row, column=0, sticky=tk.W, pady=2
                )
                
                # Field widget
                if field_type == 'entry':
                    var = getattr(self, f"{field_id}_var", None)
                    if var is None:
                        var = tk.StringVar()
                        setattr(self, f"{field_id}_var", var)
                    entry = ttk.Entry(self.dynamic_fields_container, textvariable=var, width=30, font=("Segoe UI", 10))
                    entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                    self.dynamic_fields[field_id] = entry
                    create_tooltip(entry, f"Optional: {label}")
                    
                elif field_type == 'combobox':
                    var = getattr(self, f"{field_id}_var", None)
                    if var is None:
                        var = tk.StringVar()
                        setattr(self, f"{field_id}_var", var)
                    combo = ttk.Combobox(self.dynamic_fields_container, textvariable=var, width=27)
                    if options:
                        combo['values'] = options
                    combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                    self.dynamic_fields[field_id] = combo
                    create_tooltip(combo, f"Optional: {label}")
                
                row += 1
            
            # Configure column weights
            self.dynamic_fields_container.columnconfigure(1, weight=1)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating dynamic fields: {e}", exc_info=True)
    
    def _save(self):
        """Save the asset."""
        # Validate
        if not self.deceased_var.get().strip():
            self.error_label.config(text="Please select a deceased person")
            return
        if not self.institution_var.get().strip():
            self.error_label.config(text="Please select an institution")
            return
        if not self.asset_type_var.get().strip():
            self.error_label.config(text="Please select an asset type")
            return
        
        # Find IDs
        deceased_name = self.deceased_var.get()
        deceased_id = None
        for d in self.deceased_list:
            if f"{d['FirstName']} {d['LastName']}" == deceased_name:
                deceased_id = d['DeceasedId']
                break
        
        institution_name = self.institution_var.get()
        institution_id = None
        for i in self.institutions_list:
            if i['Name'] == institution_name:
                institution_id = i['InstitutionId']
                break
        
        # Get asset type
        asset_type = self.asset_type_var.get().strip()
        
        # Get date values from date pickers
        account_opening_date = None
        last_transaction_date = None
        maturity_date = None
        policy_start_date = None
        policy_end_date = None
        
        if hasattr(self, 'account_opening_picker'):
            account_opening = self.account_opening_picker.get()
            if account_opening and account_opening != "YYYY-MM-DD":
                try:
                    import datetime
                    account_opening_date = datetime.datetime.strptime(account_opening, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        if hasattr(self, 'last_transaction_picker'):
            last_transaction = self.last_transaction_picker.get()
            if last_transaction and last_transaction != "YYYY-MM-DD":
                try:
                    import datetime
                    last_transaction_date = datetime.datetime.strptime(last_transaction, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        if hasattr(self, 'maturity_picker'):
            maturity = self.maturity_picker.get()
            if maturity and maturity != "YYYY-MM-DD":
                try:
                    import datetime
                    maturity_date = datetime.datetime.strptime(maturity, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        if hasattr(self, 'policy_start_date_picker'):
            policy_start = self.policy_start_date_picker.get()
            if policy_start and policy_start != "YYYY-MM-DD":
                try:
                    import datetime
                    policy_start_date = datetime.datetime.strptime(policy_start, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        if hasattr(self, 'policy_end_date_picker'):
            policy_end = self.policy_end_date_picker.get()
            if policy_end and policy_end != "YYYY-MM-DD":
                try:
                    import datetime
                    policy_end_date = datetime.datetime.strptime(policy_end, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        # Prepare asset data with all detail table fields
        asset_data = {
            "DeceasedId": deceased_id,
            "InstitutionId": institution_id,
            "AssetType": asset_type,
            "Identifier": self.identifier_var.get().strip() or None,
            "EstimatedValue": float(self.value_var.get()) if self.value_var.get().strip() else None,
            # Bank Account fields
            "AccountStatus": self.account_status_var.get().strip() or None if hasattr(self, 'account_status_var') else None,
            "AccountOpeningDate": account_opening_date,
            "LastTransactionDate": last_transaction_date,
            "InterestRate": float(self.interest_rate_var.get().strip()) if hasattr(self, 'interest_rate_var') and self.interest_rate_var.get().strip() else None,
            "AccountHolderName": self.account_holder_var.get().strip() or None if hasattr(self, 'account_holder_var') else None,
            "BranchLocation": self.branch_var.get().strip() or None if hasattr(self, 'branch_var') else None,
            "Currency": self.currency_var.get().strip() or "USD" if hasattr(self, 'currency_var') else "USD",
            # Vehicle fields
            "VehicleMake": self.vehicle_make_var.get().strip() or None if hasattr(self, 'vehicle_make_var') else None,
            "VehicleModel": self.vehicle_model_var.get().strip() or None if hasattr(self, 'vehicle_model_var') else None,
            "VehicleYear": int(self.vehicle_year_var.get().strip()) if hasattr(self, 'vehicle_year_var') and self.vehicle_year_var.get().strip() else None,
            "VehicleVIN": self.vehicle_vin_var.get().strip() or None if hasattr(self, 'vehicle_vin_var') else None,
            "VehicleRegistration": self.vehicle_registration_var.get().strip() or None if hasattr(self, 'vehicle_registration_var') else None,
            "VehicleCondition": self.vehicle_condition_var.get().strip() or None if hasattr(self, 'vehicle_condition_var') else None,
            "VehicleMileage": int(self.vehicle_mileage_var.get().strip()) if hasattr(self, 'vehicle_mileage_var') and self.vehicle_mileage_var.get().strip() else None,
            # Real Estate fields
            "PropertyAddress": self.property_address_var.get().strip() or None if hasattr(self, 'property_address_var') else None,
            "PropertyType": self.property_type_var.get().strip() or None if hasattr(self, 'property_type_var') else None,
            "PropertySize": float(self.property_size_var.get().strip()) if hasattr(self, 'property_size_var') and self.property_size_var.get().strip() else None,
            "PropertyCondition": self.property_condition_var.get().strip() or None if hasattr(self, 'property_condition_var') else None,
            "PropertyTaxId": self.property_tax_id_var.get().strip() or None if hasattr(self, 'property_tax_id_var') else None,
            # Investment fields
            "InvestmentType": self.investment_type_var.get().strip() or None if hasattr(self, 'investment_type_var') else None,
            # Insurance Policy fields
            "PolicyNumber": self.policy_number_var.get().strip() or None if hasattr(self, 'policy_number_var') else None,
            "PolicyType": self.policy_type_var.get().strip() or None if hasattr(self, 'policy_type_var') else None,
            "PolicyStartDate": policy_start_date,
            "PolicyEndDate": policy_end_date,
            "PremiumAmount": float(self.premium_amount_var.get().strip()) if hasattr(self, 'premium_amount_var') and self.premium_amount_var.get().strip() else None,
            # Common fields
            "BeneficiaryInfo": self.beneficiary_var.get().strip() or None if hasattr(self, 'beneficiary_var') else None,
            "Documentation": self.documentation_var.get().strip() or None,
            "Notes": self.notes_text.get(1.0, tk.END).strip() or None
        }
        
        # Call callback
        self.on_save(asset_data)
        self.modal.dialog.destroy()
    
    def show(self):
        """Show the modal."""
        self.modal.show()


class AddClaimantModal:
    """Modal for adding a new claimant record."""
    
    def __init__(self, parent: tk.Tk, on_save: Callable[[Dict[str, Any]], None]):
        """
        Initialize the modal.
        
        Args:
            parent: Parent window
            on_save: Callback function that receives the claimant data
        """
        self.on_save = on_save
        self.modal = ModalDialog(parent, "Add New Claimant", width=600, height=700)
        
        # Use ScrollableFrame for the form
        from ui.scrollable_frame import ScrollableFrame
        scrollable = ScrollableFrame(self.modal.content_frame)
        scrollable.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        form_frame = scrollable.inner_frame
        form_frame.configure(padding="20")
        
        row = 0
        
        # Personal Information Section
        section_label1 = ttk.Label(form_frame, text="Personal Information", font=("Segoe UI", 11, "bold"))
        section_label1.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # National ID
        ttk.Label(form_frame, text="National ID:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.national_id_var = tk.StringVar()
        national_id_entry = ttk.Entry(form_frame, textvariable=self.national_id_var, width=30, font=("Segoe UI", 10))
        national_id_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        national_id_entry.focus()
        create_tooltip(national_id_entry, "Optional: National identification number")
        row += 1
        
        # First Name (Required)
        label_frame = ttk.Frame(form_frame)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="First Name:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(2, 0))
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(form_frame, textvariable=self.first_name_var, width=30, font=("Segoe UI", 10))
        first_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(first_name_entry, "Required: First name")
        row += 1
        
        # Middle Name
        ttk.Label(form_frame, text="Middle Name:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.middle_name_var = tk.StringVar()
        middle_name_entry = ttk.Entry(form_frame, textvariable=self.middle_name_var, width=30, font=("Segoe UI", 10))
        middle_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(middle_name_entry, "Optional: Middle name")
        row += 1
        
        # Last Name (Required)
        label_frame = ttk.Frame(form_frame)
        label_frame.grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Label(label_frame, text="Last Name:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(2, 0))
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(form_frame, textvariable=self.last_name_var, width=30, font=("Segoe UI", 10))
        last_name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(last_name_entry, "Required: Last name")
        row += 1
        
        # Date of Birth
        self.dob_picker = DatePicker(form_frame, "Date of Birth:", required=False)
        self.dob_picker.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2, padx=(0, 10))
        row += 1
        
        # Gender
        ttk.Label(form_frame, text="Gender:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(form_frame, textvariable=self.gender_var, width=27, state="readonly",
                                    values=["", "Male", "Female", "Other", "Prefer not to say"])
        gender_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(gender_combo, "Optional: Gender")
        row += 1
        
        # Relationship
        ttk.Label(form_frame, text="Relationship:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.relationship_var = tk.StringVar()
        relationship_combo = ttk.Combobox(form_frame, textvariable=self.relationship_var, width=27)
        relationship_combo['values'] = ('Spouse', 'Child', 'Parent', 'Sibling', 'Other Relative', 'Executor', 'Other')
        relationship_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(relationship_combo, "Relationship to the deceased person")
        row += 1
        
        # Contact Information Section
        section_label2 = ttk.Label(form_frame, text="Contact Information", font=("Segoe UI", 11, "bold"))
        section_label2.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Email
        ttk.Label(form_frame, text="Email:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=30, font=("Segoe UI", 10))
        email_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(email_entry, "Optional: Email address")
        row += 1
        
        # Phone
        ttk.Label(form_frame, text="Phone:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_frame, textvariable=self.phone_var, width=30, font=("Segoe UI", 10))
        phone_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(phone_entry, "Optional: Phone number")
        row += 1
        
        # Contact (General)
        ttk.Label(form_frame, text="Contact:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(form_frame, textvariable=self.contact_var, width=30, font=("Segoe UI", 10))
        contact_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(contact_entry, "Optional: General contact information")
        row += 1
        
        # Address
        ttk.Label(form_frame, text="Address:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.address_var = tk.StringVar()
        address_entry = ttk.Entry(form_frame, textvariable=self.address_var, width=30, font=("Segoe UI", 10))
        address_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(address_entry, "Optional: Street, City, State, ZIP, Country")
        row += 1
        
        # Additional Information Section
        section_label3 = ttk.Label(form_frame, text="Additional Information", font=("Segoe UI", 11, "bold"))
        section_label3.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # Occupation
        ttk.Label(form_frame, text="Occupation:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.occupation_var = tk.StringVar()
        occupation_entry = ttk.Entry(form_frame, textvariable=self.occupation_var, width=30, font=("Segoe UI", 10))
        occupation_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(occupation_entry, "Optional: Current occupation")
        row += 1
        
        # Marital Status
        ttk.Label(form_frame, text="Marital Status:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.marital_status_var = tk.StringVar()
        marital_status_combo = ttk.Combobox(form_frame, textvariable=self.marital_status_var, width=27, state="readonly",
                                            values=["", "Single", "Married", "Divorced", "Widowed"])
        marital_status_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(marital_status_combo, "Optional: Marital status")
        row += 1
        
        # Alternate Contact
        ttk.Label(form_frame, text="Alternate Contact:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.alternate_contact_var = tk.StringVar()
        alternate_contact_entry = ttk.Entry(form_frame, textvariable=self.alternate_contact_var, width=30, font=("Segoe UI", 10))
        alternate_contact_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(alternate_contact_entry, "Optional: Backup contact person")
        row += 1
        
        # Relationship Proof
        ttk.Label(form_frame, text="Relationship Proof:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.relationship_proof_var = tk.StringVar()
        relationship_proof_entry = ttk.Entry(form_frame, textvariable=self.relationship_proof_var, width=30, font=("Segoe UI", 10))
        relationship_proof_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(relationship_proof_entry, "Optional: Document reference proving relationship")
        row += 1
        
        # Notes
        ttk.Label(form_frame, text="Notes:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.notes_text = tk.Text(form_frame, width=30, height=3, font=("Segoe UI", 10))
        self.notes_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        create_tooltip(self.notes_text, "Optional: Additional information or remarks")
        row += 1
        
        # Error label
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.grid(row=row, column=0, columnspan=2, pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        self.modal.add_button("Cancel", style="default")
        self.modal.add_button("Save", self._save, style="primary")
    
    def _save(self):
        """Save the claimant."""
        # Validate
        if not self.first_name_var.get().strip():
            self.error_label.config(text="First Name is required")
            return
        if not self.last_name_var.get().strip():
            self.error_label.config(text="Last Name is required")
            return
        
        # Get date value
        dob_value = self.dob_picker.get() if self.dob_picker.get() and self.dob_picker.get() != "YYYY-MM-DD" else None
        
        # Get notes
        notes = self.notes_text.get(1.0, tk.END).strip() or None
        
        # Prepare claimant data
        claimant_data = {
            "NationalId": self.national_id_var.get().strip() or None,
            "FirstName": self.first_name_var.get().strip(),
            "MiddleName": self.middle_name_var.get().strip() or None,
            "LastName": self.last_name_var.get().strip(),
            "DateOfBirth": dob_value,
            "Gender": self.gender_var.get().strip() or None,
            "Relationship": self.relationship_var.get().strip() or None,
            "Contact": self.contact_var.get().strip() or None,
            "Email": self.email_var.get().strip() or None,
            "Phone": self.phone_var.get().strip() or None,
            "Address": self.address_var.get().strip() or None,
            "Occupation": self.occupation_var.get().strip() or None,
            "MaritalStatus": self.marital_status_var.get().strip() or None,
            "AlternateContact": self.alternate_contact_var.get().strip() or None,
            "RelationshipProof": self.relationship_proof_var.get().strip() or None,
            "Notes": notes
        }
        
        # Call callback
        self.on_save(claimant_data)
        self.modal.dialog.destroy()
    
    def show(self):
        """Show the modal."""
        self.modal.show()


