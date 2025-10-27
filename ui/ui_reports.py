"""
FARVS Reports and Analytics Module
==================================

This module provides reporting and analytics functionality for the FARVS system
through a Tkinter interface.

Structure:
- ReportsWindow: Main window class for reports and analytics
- Dashboard: Summary statistics and key metrics
- Report generation: Various report types (pending claims, asset summaries, etc.)
- Data visualization: Charts and tables for data analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any
import datetime
import csv

# Import database models (will be implemented)
# from db.models_deceased import DeceasedModel
# from db.models_assets import AssetsModel
# from db.models_claims import ClaimsModel
# from db.models_claimants import ClaimantsModel


class ReportsWindow:
    """
    Tkinter window for reports and analytics functionality.
    
    Features:
    - Dashboard with key metrics
    - Pending claims report
    - Asset summary reports
    - Deceased persons statistics
    - Export functionality (CSV, PDF)
    - Date range filtering
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Initialize the reports and analytics window.
        
        Args:
            parent: Parent Tkinter window
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Reports & Analytics")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 700)
        
        # Data storage
        self.report_data: Dict[str, Any] = {}
        
        # Initialize database models (placeholder)
        # self.deceased_model = DeceasedModel()
        # self.assets_model = AssetsModel()
        # self.claims_model = ClaimsModel()
        # self.claimants_model = ClaimantsModel()
        
        self._setup_ui()
        self._load_dashboard_data()
    
    def _setup_ui(self):
        """Create and layout the user interface components."""
        # Create notebook for different report types
        notebook = ttk.Notebook(self.window)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Dashboard tab
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Dashboard")
        self._setup_dashboard_tab(dashboard_frame)
        
        # Claims Reports tab
        claims_frame = ttk.Frame(notebook)
        notebook.add(claims_frame, text="Claims Reports")
        self._setup_claims_reports_tab(claims_frame)
        
        # Assets Reports tab
        assets_frame = ttk.Frame(notebook)
        notebook.add(assets_frame, text="Assets Reports")
        self._setup_assets_reports_tab(assets_frame)
        
        # Statistics tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        self._setup_statistics_tab(stats_frame)
    
    def _setup_dashboard_tab(self, parent: ttk.Frame):
        """Setup the dashboard tab with key metrics."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="FARVS Dashboard", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Key metrics cards
        self._create_metrics_cards(main_frame)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(main_frame, text="Recent Activity", padding="10")
        activity_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Activity treeview
        self._create_activity_treeview(activity_frame)
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh Dashboard", command=self._load_dashboard_data)
        refresh_btn.grid(row=3, column=0, columnspan=3, pady=(20, 0))
    
    def _setup_claims_reports_tab(self, parent: ttk.Frame):
        """Setup the claims reports tab."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Report controls
        controls_frame = ttk.LabelFrame(main_frame, text="Report Controls", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Date range selection
        ttk.Label(controls_frame, text="Date Range:").grid(row=0, column=0, padx=(0, 5))
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        
        ttk.Label(controls_frame, text="From:").grid(row=0, column=1, padx=(10, 5))
        start_date_entry = ttk.Entry(controls_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(controls_frame, text="To:").grid(row=0, column=3, padx=(10, 5))
        end_date_entry = ttk.Entry(controls_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.grid(row=0, column=4, padx=(0, 10))
        
        # Report type selection
        ttk.Label(controls_frame, text="Report Type:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        self.report_type_var = tk.StringVar()
        report_combo = ttk.Combobox(controls_frame, textvariable=self.report_type_var, width=20, state="readonly")
        report_combo['values'] = ('Pending Claims', 'Verified Claims', 'Settled Claims', 'All Claims')
        report_combo.set('Pending Claims')
        report_combo.grid(row=1, column=1, columnspan=2, pady=(10, 0), padx=(10, 0))
        
        # Generate and export buttons
        generate_btn = ttk.Button(controls_frame, text="Generate Report", command=self._generate_claims_report)
        generate_btn.grid(row=1, column=3, padx=(10, 5), pady=(10, 0))
        
        export_btn = ttk.Button(controls_frame, text="Export CSV", command=self._export_claims_csv)
        export_btn.grid(row=1, column=4, padx=(5, 0), pady=(10, 0))
        
        # Report results
        results_frame = ttk.LabelFrame(main_frame, text="Report Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Claims treeview
        self._create_claims_report_treeview(results_frame)
    
    def _setup_assets_reports_tab(self, parent: ttk.Frame):
        """Setup the assets reports tab."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Report controls
        controls_frame = ttk.LabelFrame(main_frame, text="Asset Report Controls", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Asset type filter
        ttk.Label(controls_frame, text="Asset Type:").grid(row=0, column=0, padx=(0, 5))
        self.asset_type_filter_var = tk.StringVar()
        asset_type_combo = ttk.Combobox(controls_frame, textvariable=self.asset_type_filter_var, width=20, state="readonly")
        asset_type_combo['values'] = ('All', 'Bank Account', 'Investment', 'Insurance Policy', 'Real Estate', 'Vehicle', 'Other')
        asset_type_combo.set('All')
        asset_type_combo.grid(row=0, column=1, padx=(10, 0))
        
        # Institution filter
        ttk.Label(controls_frame, text="Institution:").grid(row=0, column=2, padx=(20, 5))
        self.institution_filter_var = tk.StringVar()
        institution_combo = ttk.Combobox(controls_frame, textvariable=self.institution_filter_var, width=20, state="readonly")
        institution_combo['values'] = ('All', 'National Bank', 'State Insurance')
        institution_combo.set('All')
        institution_combo.grid(row=0, column=3, padx=(10, 0))
        
        # Generate and export buttons
        generate_btn = ttk.Button(controls_frame, text="Generate Report", command=self._generate_assets_report)
        generate_btn.grid(row=0, column=4, padx=(20, 5))
        
        export_btn = ttk.Button(controls_frame, text="Export CSV", command=self._export_assets_csv)
        export_btn.grid(row=0, column=5, padx=(5, 0))
        
        # Report results
        results_frame = ttk.LabelFrame(main_frame, text="Asset Report Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Assets treeview
        self._create_assets_report_treeview(results_frame)
    
    def _setup_statistics_tab(self, parent: ttk.Frame):
        """Setup the statistics tab."""
        # Main container
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Statistics summary
        stats_frame = ttk.LabelFrame(main_frame, text="System Statistics", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Statistics labels
        self._create_statistics_labels(stats_frame)
        
        # Charts frame (placeholder for future chart implementation)
        charts_frame = ttk.LabelFrame(main_frame, text="Charts & Visualizations", padding="10")
        charts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Placeholder for charts
        chart_placeholder = ttk.Label(charts_frame, text="Chart visualization will be implemented here\n(Matplotlib integration planned)")
        chart_placeholder.grid(row=0, column=0, pady=50)
    
    def _create_metrics_cards(self, parent: ttk.Frame):
        """Create metric cards for the dashboard."""
        # Configure grid for cards
        for i in range(3):
            parent.columnconfigure(i, weight=1)
        
        # Total Deceased
        deceased_card = ttk.LabelFrame(parent, text="Total Deceased", padding="10")
        deceased_card.grid(row=1, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        self.deceased_count_label = ttk.Label(deceased_card, text="0", font=("Arial", 24, "bold"))
        self.deceased_count_label.grid(row=0, column=0)
        
        # Total Assets
        assets_card = ttk.LabelFrame(parent, text="Total Assets", padding="10")
        assets_card.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.assets_count_label = ttk.Label(assets_card, text="0", font=("Arial", 24, "bold"))
        self.assets_count_label.grid(row=0, column=0)
        
        # Pending Claims
        claims_card = ttk.LabelFrame(parent, text="Pending Claims", padding="10")
        claims_card.grid(row=1, column=2, padx=(10, 0), sticky=(tk.W, tk.E))
        
        self.claims_count_label = ttk.Label(claims_card, text="0", font=("Arial", 24, "bold"))
        self.claims_count_label.grid(row=0, column=0)
    
    def _create_activity_treeview(self, parent: ttk.Frame):
        """Create the activity treeview."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("Date", "Activity", "Details")
        self.activity_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # Configure column headings and widths
        column_widths = {"Date": 100, "Activity": 150, "Details": 300}
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.activity_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_claims_report_treeview(self, parent: ttk.Frame):
        """Create the claims report treeview."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("Claim ID", "Asset", "Claimant", "Status", "Filed Date", "Value")
        self.claims_report_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"Claim ID": 80, "Asset": 200, "Claimant": 150, "Status": 100, "Filed Date": 100, "Value": 100}
        for col in columns:
            self.claims_report_tree.heading(col, text=col)
            self.claims_report_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claims_report_tree.yview)
        self.claims_report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.claims_report_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_assets_report_treeview(self, parent: ttk.Frame):
        """Create the assets report treeview."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("Asset ID", "Deceased", "Type", "Institution", "Identifier", "Value", "Claims")
        self.assets_report_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"Asset ID": 80, "Deceased": 150, "Type": 120, "Institution": 150, "Identifier": 120, "Value": 100, "Claims": 80}
        for col in columns:
            self.assets_report_tree.heading(col, text=col)
            self.assets_report_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.assets_report_tree.yview)
        self.assets_report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.assets_report_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_statistics_labels(self, parent: ttk.Frame):
        """Create statistics labels."""
        # Configure grid
        for i in range(2):
            parent.columnconfigure(i, weight=1)
        
        # Left column
        ttk.Label(parent, text="Total Deceased Persons:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.total_deceased_label = ttk.Label(parent, text="0")
        self.total_deceased_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Total Assets:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.total_assets_label = ttk.Label(parent, text="0")
        self.total_assets_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Total Asset Value:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.total_value_label = ttk.Label(parent, text="$0.00")
        self.total_value_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Total Claims:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.total_claims_label = ttk.Label(parent, text="0")
        self.total_claims_label.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Pending Claims:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.pending_claims_label = ttk.Label(parent, text="0")
        self.pending_claims_label.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Settled Claims:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=2)
        self.settled_claims_label = ttk.Label(parent, text="0")
        self.settled_claims_label.grid(row=5, column=1, sticky=tk.W, pady=2)
    
    def _load_dashboard_data(self):
        """Load dashboard data and update metrics."""
        try:
            # TODO: Replace with actual database calls
            # deceased_count = self.deceased_model.count()
            # assets_count = self.assets_model.count()
            # claims_count = self.claims_model.count_pending()
            
            # Placeholder data
            deceased_count = 2
            assets_count = 2
            claims_count = 1
            
            # Update metric labels
            self.deceased_count_label.config(text=str(deceased_count))
            self.assets_count_label.config(text=str(assets_count))
            self.claims_count_label.config(text=str(claims_count))
            
            # Load recent activity
            self._load_recent_activity()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard data: {e}")
    
    def _load_recent_activity(self):
        """Load recent activity data."""
        try:
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # TODO: Replace with actual database call
            # activities = self.get_recent_activities()
            
            # Placeholder activity data
            activities = [
                ("2024-01-20", "New Claim Filed", "Mary Doe filed claim for Bank Account ACC-123456"),
                ("2024-01-19", "Asset Added", "Insurance Policy POL-789012 added for Jane Smith"),
                ("2024-01-18", "Deceased Record Added", "John Doe record created"),
                ("2024-01-17", "Claim Verified", "Robert Smith's claim verified"),
            ]
            
            # Populate treeview
            for activity in activities:
                self.activity_tree.insert("", tk.END, values=activity)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recent activity: {e}")
    
    def _generate_claims_report(self):
        """Generate claims report based on selected criteria."""
        try:
            # Clear existing items
            for item in self.claims_report_tree.get_children():
                self.claims_report_tree.delete(item)
            
            # Get report criteria
            report_type = self.report_type_var.get()
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            # TODO: Replace with actual database call
            # claims = self.claims_model.get_report_data(report_type, start_date, end_date)
            
            # Placeholder claims data
            claims = [
                (1, "Bank Account - ACC-123456 (John Doe)", "Mary Doe", "Pending", "2024-01-15", "$50,000.00"),
                (2, "Insurance Policy - POL-789012 (Jane Smith)", "Robert Smith", "Verified", "2024-01-10", "$100,000.00"),
            ]
            
            # Filter by report type
            if report_type != "All Claims":
                status_filter = report_type.replace(" Claims", "")
                claims = [c for c in claims if c[3] == status_filter]
            
            # Populate treeview
            for claim in claims:
                self.claims_report_tree.insert("", tk.END, values=claim)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate claims report: {e}")
    
    def _generate_assets_report(self):
        """Generate assets report based on selected criteria."""
        try:
            # Clear existing items
            for item in self.assets_report_tree.get_children():
                self.assets_report_tree.delete(item)
            
            # Get report criteria
            asset_type = self.asset_type_filter_var.get()
            institution = self.institution_filter_var.get()
            
            # TODO: Replace with actual database call
            # assets = self.assets_model.get_report_data(asset_type, institution)
            
            # Placeholder assets data
            assets = [
                (1, "John Doe", "Bank Account", "National Bank", "ACC-123456", "$50,000.00", 1),
                (2, "Jane Smith", "Insurance Policy", "State Insurance", "POL-789012", "$100,000.00", 1),
            ]
            
            # Filter by criteria
            if asset_type != "All":
                assets = [a for a in assets if a[2] == asset_type]
            
            if institution != "All":
                assets = [a for a in assets if a[3] == institution]
            
            # Populate treeview
            for asset in assets:
                self.assets_report_tree.insert("", tk.END, values=asset)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate assets report: {e}")
    
    def _export_claims_csv(self):
        """Export claims report to CSV file."""
        try:
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Claims Report"
            )
            
            if not file_path:
                return
            
            # Get data from treeview
            data = []
            for item in self.claims_report_tree.get_children():
                values = self.claims_report_tree.item(item)['values']
                data.append(values)
            
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Claim ID", "Asset", "Claimant", "Status", "Filed Date", "Value"])
                writer.writerows(data)
            
            messagebox.showinfo("Success", f"Claims report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export claims report: {e}")
    
    def _export_assets_csv(self):
        """Export assets report to CSV file."""
        try:
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Assets Report"
            )
            
            if not file_path:
                return
            
            # Get data from treeview
            data = []
            for item in self.assets_report_tree.get_children():
                values = self.assets_report_tree.item(item)['values']
                data.append(values)
            
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Asset ID", "Deceased", "Type", "Institution", "Identifier", "Value", "Claims"])
                writer.writerows(data)
            
            messagebox.showinfo("Success", f"Assets report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export assets report: {e}")
