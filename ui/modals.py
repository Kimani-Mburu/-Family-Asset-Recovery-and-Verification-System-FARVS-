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
    """Modal for adding a new asset record."""
    
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
        self.modal = ModalDialog(parent, "Add New Asset", width=500, height=450)
        
        # Form fields
        form_frame = ttk.Frame(self.modal.content_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Deceased Person
        ttk.Label(form_frame, text="Deceased Person:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.deceased_var = tk.StringVar()
        deceased_names = [f"{d['FirstName']} {d['LastName']}" for d in deceased_list]
        self.deceased_combo = ttk.Combobox(form_frame, textvariable=self.deceased_var, width=27, state="readonly")
        self.deceased_combo['values'] = deceased_names
        self.deceased_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.deceased_combo.focus()
        
        # Institution
        ttk.Label(form_frame, text="Institution:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.institution_var = tk.StringVar()
        institution_names = [i['Name'] for i in institutions_list]
        self.institution_combo = ttk.Combobox(form_frame, textvariable=self.institution_var, width=27, state="readonly")
        self.institution_combo['values'] = institution_names
        self.institution_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Asset Type
        ttk.Label(form_frame, text="Asset Type:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.asset_type_var = tk.StringVar()
        asset_type_combo = ttk.Combobox(form_frame, textvariable=self.asset_type_var, width=27)
        asset_type_combo['values'] = ('Bank Account', 'Investment', 'Insurance Policy', 'Real Estate', 'Vehicle', 'Other')
        asset_type_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Identifier
        ttk.Label(form_frame, text="Account/Policy ID:", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.identifier_var = tk.StringVar()
        identifier_entry = ttk.Entry(form_frame, textvariable=self.identifier_var, width=30, font=("Segoe UI", 10))
        identifier_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Estimated Value
        ttk.Label(form_frame, text="Estimated Value:", font=("Segoe UI", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(form_frame, textvariable=self.value_var, width=30, font=("Segoe UI", 10))
        value_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(form_frame, text="(USD)", font=("Segoe UI", 8)).grid(row=4, column=2, sticky=tk.W, padx=(5, 0))
        
        # Error label
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        self.modal.add_button("Cancel", style="default")
        self.modal.add_button("Save", self._save, style="primary")
    
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
        
        # Prepare asset data
        asset_data = {
            "DeceasedId": deceased_id,
            "InstitutionId": institution_id,
            "AssetType": self.asset_type_var.get().strip(),
            "Identifier": self.identifier_var.get().strip() or None,
            "EstimatedValue": float(self.value_var.get()) if self.value_var.get().strip() else None
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
        self.modal = ModalDialog(parent, "Add New Claimant", width=500, height=450)
        
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
        national_id_entry.focus()
        
        # First Name
        ttk.Label(form_frame, text="First Name:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(form_frame, textvariable=self.first_name_var, width=30, font=("Segoe UI", 10))
        first_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Last Name
        ttk.Label(form_frame, text="Last Name:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(form_frame, textvariable=self.last_name_var, width=30, font=("Segoe UI", 10))
        last_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Relationship
        ttk.Label(form_frame, text="Relationship:", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.relationship_var = tk.StringVar()
        relationship_combo = ttk.Combobox(form_frame, textvariable=self.relationship_var, width=27)
        relationship_combo['values'] = ('Spouse', 'Child', 'Parent', 'Sibling', 'Other Relative', 'Executor', 'Other')
        relationship_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Contact
        ttk.Label(form_frame, text="Contact:", font=("Segoe UI", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(form_frame, textvariable=self.contact_var, width=30, font=("Segoe UI", 10))
        contact_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Error label
        self.error_label = ttk.Label(form_frame, text="", foreground="red")
        self.error_label.grid(row=5, column=0, columnspan=2, pady=10)
        
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
        
        # Prepare claimant data
        claimant_data = {
            "NationalId": self.national_id_var.get().strip() or None,
            "FirstName": self.first_name_var.get().strip(),
            "LastName": self.last_name_var.get().strip(),
            "Relationship": self.relationship_var.get().strip() or None,
            "Contact": self.contact_var.get().strip() or None
        }
        
        # Call callback
        self.on_save(claimant_data)
        self.modal.dialog.destroy()
    
    def show(self):
        """Show the modal."""
        self.modal.show()


