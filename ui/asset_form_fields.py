"""
Dynamic Asset Form Fields
==========================

Provides dynamic form field generation based on asset type.
Different asset types (Bank Account, Vehicle, Real Estate, etc.) 
have different relevant fields.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple, Optional
from ui.components import DatePicker, create_tooltip


class AssetFormFields:
    """Manages dynamic form fields based on asset type."""
    
    # Field definitions for each asset type
    FIELD_DEFINITIONS = {
        'Bank Account': {
            'fields': [
                ('account_status', 'Account Status', 'combobox', ['Active', 'Inactive', 'Closed', 'Dormant', 'Unknown']),
                ('account_opening_date', 'Account Opening Date', 'datepicker', None),
                ('last_transaction_date', 'Last Transaction Date', 'datepicker', None),
                ('interest_rate', 'Interest Rate (%)', 'entry', None),
                ('account_holder_name', 'Account Holder Name', 'entry', None),
                ('branch_location', 'Branch/Location', 'entry', None),
                ('currency', 'Currency', 'combobox', ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'Other']),
                ('beneficiary_info', 'Beneficiary Info', 'entry', None),
            ],
            'hide_fields': ['maturity_date', 'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 
                          'vehicle_registration', 'property_address', 'property_type', 'property_size']
        },
        'Vehicle': {
            'fields': [
                ('vehicle_make', 'Make', 'entry', None),
                ('vehicle_model', 'Model', 'entry', None),
                ('vehicle_year', 'Year', 'entry', None),
                ('vehicle_vin', 'VIN', 'entry', None),
                ('vehicle_registration', 'Registration Number', 'entry', None),
                ('vehicle_condition', 'Condition', 'combobox', ['Excellent', 'Good', 'Fair', 'Poor', 'Unknown']),
                ('vehicle_mileage', 'Mileage', 'entry', None),
            ],
            'hide_fields': ['account_status', 'account_opening_date', 'last_transaction_date', 'interest_rate',
                          'maturity_date', 'account_holder_name', 'branch_location', 'currency', 'beneficiary_info',
                          'property_address', 'property_type', 'property_size']
        },
        'Real Estate': {
            'fields': [
                ('property_address', 'Property Address', 'entry', None),
                ('property_type', 'Property Type', 'combobox', ['Residential', 'Commercial', 'Land', 'Other']),
                ('property_size', 'Size (sq ft)', 'entry', None),
                ('property_condition', 'Condition', 'combobox', ['Excellent', 'Good', 'Fair', 'Poor', 'Unknown']),
                ('property_tax_id', 'Tax ID/Assessor ID', 'entry', None),
            ],
            'hide_fields': ['account_status', 'account_opening_date', 'last_transaction_date', 'interest_rate',
                          'maturity_date', 'account_holder_name', 'branch_location', 'currency', 'beneficiary_info',
                          'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 'vehicle_registration']
        },
        'Investment': {
            'fields': [
                ('account_status', 'Account Status', 'combobox', ['Active', 'Inactive', 'Closed', 'Dormant', 'Unknown']),
                ('account_opening_date', 'Account Opening Date', 'datepicker', None),
                ('maturity_date', 'Maturity Date', 'datepicker', None),
                ('interest_rate', 'Interest Rate (%)', 'entry', None),
                ('currency', 'Currency', 'combobox', ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'Other']),
                ('beneficiary_info', 'Beneficiary Info', 'entry', None),
            ],
            'hide_fields': ['last_transaction_date', 'account_holder_name', 'branch_location',
                          'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 'vehicle_registration',
                          'property_address', 'property_type', 'property_size']
        },
        'Insurance Policy': {
            'fields': [
                ('policy_number', 'Policy Number', 'entry', None),
                ('policy_type', 'Policy Type', 'combobox', ['Life', 'Health', 'Property', 'Auto', 'Other']),
                ('policy_start_date', 'Policy Start Date', 'datepicker', None),
                ('policy_end_date', 'Policy End Date', 'datepicker', None),
                ('premium_amount', 'Premium Amount', 'entry', None),
                ('beneficiary_info', 'Beneficiary Info', 'entry', None),
            ],
            'hide_fields': ['account_status', 'account_opening_date', 'last_transaction_date', 'interest_rate',
                          'maturity_date', 'account_holder_name', 'branch_location', 'currency',
                          'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 'vehicle_registration',
                          'property_address', 'property_type', 'property_size']
        },
        'Other': {
            'fields': [
                ('description', 'Description', 'text', None),
            ],
            'hide_fields': ['account_status', 'account_opening_date', 'last_transaction_date', 'interest_rate',
                          'maturity_date', 'account_holder_name', 'branch_location', 'currency', 'beneficiary_info',
                          'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 'vehicle_registration',
                          'property_address', 'property_type', 'property_size']
        }
    }
    
    @staticmethod
    def get_fields_for_type(asset_type: str) -> List[Tuple]:
        """Get field definitions for a specific asset type."""
        return AssetFormFields.FIELD_DEFINITIONS.get(asset_type, {}).get('fields', [])
    
    @staticmethod
    def get_hide_fields_for_type(asset_type: str) -> List[str]:
        """Get list of fields to hide for a specific asset type."""
        return AssetFormFields.FIELD_DEFINITIONS.get(asset_type, {}).get('hide_fields', [])

