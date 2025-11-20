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

# Import database models
from db.models_deceased import DeceasedModel
from db.models_assets import AssetsModel
from db.models_claims import ClaimsModel
from db.models_claimants import ClaimantsModel
from db.models_institutions import InstitutionsModel


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
    
    def __init__(self, parent: tk.Tk, container: Optional[ttk.Frame] = None):
        """
        Initialize the reports and analytics window.
        
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
            self.window.title("Reports & Analytics")
            self.window.geometry("1200x800")
            self.window.minsize(1000, 700)
        
        # Data storage
        self.report_data: Dict[str, Any] = {}
        
        # Initialize database models
        self.deceased_model = DeceasedModel()
        self.assets_model = AssetsModel()
        self.claims_model = ClaimsModel()
        self.claimants_model = ClaimantsModel()
        self.institutions_model = InstitutionsModel()
        
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
        # CRITICAL: Configure for proper expansion
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
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
        
        # Date range selection with DatePickers
        from ui.components import DatePicker
        ttk.Label(controls_frame, text="Date Range:").grid(row=0, column=0, padx=(0, 5))
        
        self.start_date_picker = DatePicker(controls_frame, "From:", required=False)
        self.start_date_picker.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(10, 10))
        
        self.end_date_picker = DatePicker(controls_frame, "To:", required=False)
        self.end_date_picker.grid(row=0, column=3, columnspan=2, sticky=tk.W, padx=(10, 10))
        
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
        # CRITICAL: Configure for proper expansion
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
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
        # CRITICAL: Configure for proper expansion
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
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
        
        # Charts frame (reserved for future chart implementation with Matplotlib)
        charts_frame = ttk.LabelFrame(main_frame, text="Charts & Visualizations", padding="10")
        charts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Information message about chart feature
        chart_info = ttk.Label(
            charts_frame,
            text="Chart visualization feature\n(Matplotlib integration planned for future release)",
            font=("Segoe UI", 10),
            foreground="#6B7280"
        )
        chart_info.grid(row=0, column=0, pady=50)
    
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
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.activity_tree, tree_frame)
    
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
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.claims_report_tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.claims_report_tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.claims_report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.claims_report_tree, tree_frame)
    
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
        
        # Scrollbar - CORRECT PATTERN: command links scrollbar to treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.assets_report_tree.yview)
        # CORRECT PATTERN: yscrollcommand links treeview to scrollbar
        self.assets_report_tree.configure(yscrollcommand=scrollbar.set)
        
        # CORRECT PATTERN: Use pack() for treeview and scrollbar (as per Tkinter best practices)
        self.assets_report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enhanced mousewheel scrolling
        from ui.scroll_utils import configure_treeview_scrolling
        configure_treeview_scrolling(self.assets_report_tree, tree_frame)
    
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
        
        # Load statistics on initialization
        self._load_statistics()
    
    def _load_dashboard_data(self):
        """Load dashboard data and update metrics."""
        try:
            # Load statistics from database
            deceased_count = self.deceased_model.count()
            assets_count = self.assets_model.count()
            claims_count = self.claims_model.count_by_status('Pending')
            
            # Update metric labels
            self.deceased_count_label.config(text=str(deceased_count))
            self.assets_count_label.config(text=str(assets_count))
            self.claims_count_label.config(text=str(claims_count))
            
            # Load recent activity
            self._load_recent_activity()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard data: {e}")
    
    def _load_statistics(self):
        """Load and display statistics."""
        try:
            # Load statistics
            total_deceased = self.deceased_model.count()
            total_assets = self.assets_model.count()
            total_claims = len(self.claims_model.get_all_with_details())
            pending_claims = len(self.claims_model.get_by_status('Pending'))
            settled_claims = len(self.claims_model.get_by_status('Settled'))
            
            # Calculate total asset value
            assets = self.assets_model.get_all_with_details()
            total_value = sum(asset.get('EstimatedValue', 0) or 0 for asset in assets)
            
            # Update labels
            self.total_deceased_label.config(text=str(total_deceased))
            self.total_assets_label.config(text=str(total_assets))
            self.total_claims_label.config(text=str(total_claims))
            self.pending_claims_label.config(text=str(pending_claims))
            self.settled_claims_label.config(text=str(settled_claims))
            self.total_value_label.config(text=f"${total_value:,.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {e}")
    
    def _load_recent_activity(self):
        """Load recent activity data."""
        try:
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Load recent activities from claims
            activities = []
            try:
                # Get recent claims as activity
                recent_claims = self.claims_model.get_all_with_details()[:10]
                for claim in recent_claims:
                    # Get filed date
                    filed_date = claim.get('FiledAt')
                    if filed_date:
                        if isinstance(filed_date, datetime.datetime):
                            activity_date = filed_date.strftime('%Y-%m-%d')
                        else:
                            activity_date = str(filed_date)[:10]
                    else:
                        activity_date = 'N/A'
                    
                    activity_type = f"Claim {claim.get('Status', 'Filed')}"
                    
                    # Get claimant name
                    claimant_first = claim.get('ClaimantFirstName', '')
                    claimant_last = claim.get('ClaimantLastName', '')
                    claimant_name = f"{claimant_first} {claimant_last}".strip() or 'Unknown'
                    # Get asset type
                    asset_type = claim.get('AssetType', 'Asset')
                    activity_desc = f"{claimant_name} - {asset_type}"
                    activities.append((activity_date, activity_type, activity_desc))
            except Exception:
                # If audit log query fails, show empty list
                pass
            
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
            start_date = self.start_date_picker.value.get() if hasattr(self, 'start_date_picker') else ""
            end_date = self.end_date_picker.value.get() if hasattr(self, 'end_date_picker') else ""
            
            # Load claims from database
            if report_type == "All Claims":
                claims_data = self.claims_model.get_all_with_details()
            elif report_type == "Pending Claims":
                claims_data = self.claims_model.get_by_status('Pending')
            elif report_type == "Verified Claims":
                claims_data = self.claims_model.get_by_status('Verified')
            elif report_type == "Settled Claims":
                claims_data = self.claims_model.get_by_status('Settled')
            else:
                claims_data = self.claims_model.get_all_with_details()
            
            # Format claims data for display
            claims = []
            for claim in claims_data:
                # Get asset type and identifier
                asset_type = claim.get('AssetType', 'Unknown')
                asset_identifier = claim.get('Identifier', 'N/A')
                # Get deceased name
                deceased_first = claim.get('DeceasedFirstName', '')
                deceased_last = claim.get('DeceasedLastName', '')
                deceased_name = f"{deceased_first} {deceased_last}".strip() or 'Unknown'
                # Build asset description
                asset_desc = f"{asset_type} - {asset_identifier} ({deceased_name})"
                # Get filed date
                filed_date = claim.get('FiledAt', datetime.datetime.now())
                if isinstance(filed_date, datetime.datetime):
                    filed_date = filed_date.strftime('%Y-%m-%d')
                elif filed_date:
                    filed_date = str(filed_date)[:10]
                else:
                    filed_date = 'N/A'
                # Get value
                value = claim.get('EstimatedValue', 0)
                value_str = f"${value:,.2f}" if value else "$0.00"
                # Get claimant name
                claimant_first = claim.get('ClaimantFirstName', '')
                claimant_last = claim.get('ClaimantLastName', '')
                claimant_name = f"{claimant_first} {claimant_last}".strip() or 'Unknown'
                
                claims.append((
                    claim.get('ClaimId', 0),
                    asset_desc,
                    claimant_name,
                    claim.get('Status', 'Unknown'),
                    filed_date,
                    value_str
                ))
            
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
            
            # Load assets from database
            if asset_type == "All Types" and institution == "All Institutions":
                assets_data = self.assets_model.get_all_with_details()
            elif asset_type != "All Types":
                assets_data = self.assets_model.get_by_type(asset_type)
            else:
                assets_data = self.assets_model.get_all_with_details()
            
            # Format assets data for display
            assets = []
            for asset in assets_data:
                # Format asset value
                value = f"${asset.get('EstimatedValue', 0):,.2f}" if asset.get('EstimatedValue') else "$0.00"
                # Count claims for this asset (simplified - in production use proper join)
                claim_count = 0  # Could be enhanced with proper query
                
                assets.append((
                    asset.get('AssetId', 0),
                    asset.get('DeceasedName', 'Unknown'),
                    asset.get('AssetType', 'Unknown'),
                    asset.get('InstitutionName', 'Unknown'),
                    asset.get('Identifier', 'N/A'),
                    value,
                    claim_count
                ))
            
            # Filter by institution if specified
            if institution != "All Institutions":
                # Extract institution name from filter
                inst_name = institution.split(' (')[0] if ' (' in institution else institution
                assets = [a for a in assets if a[3] == inst_name]
            
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
