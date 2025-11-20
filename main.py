"""
FARVS Main Application Entry Point
===================================

This module provides the main Tkinter application window with integrated
login, sidebar navigation, and tabbed interface for all FARVS modules.

Structure:
- MainWindow: Single window application with sidebar and tabs
- Integrated login: Login form in main window
- Sidebar navigation: Quick access to crucial parts
- Tabbed modules: All modules in one window with tabs
- Profile/Settings: User profile and application settings
- Modern UI: Blue and white theme with improved layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import secrets
from typing import Optional

# Import database connection utilities
from db.db_connect import try_connect
from config import get_env
from logging_config import setup_logging, get_logger

# Setup logging early
logger = get_logger(__name__)
from auth.session import set_current_user, get_current_user
from auth.password import hash_password, verify_password, hash_password_legacy
from db.models_users import UsersModel
from ui.theme import set_theme

# Setup logging (enable debug mode via environment variable)
DEBUG_MODE = get_env('DEBUG', 'false').lower() == 'true'
setup_logging(debug=DEBUG_MODE)
logger = get_logger(__name__)


class MainWindow:
    """
    Main application window with sidebar, integrated login and tabbed interface.
    
    Features:
    - Single window design (no separate dialogs)
    - Sidebar navigation for crucial parts
    - Integrated login form
    - Tabbed interface for all modules
    - Profile/Settings button
    - Database connection status
    - Modern blue and white theme
    """
    
    def __init__(self):
        """Initialize the main application window."""
        logger.info("Initializing MainWindow")
        self.root = tk.Tk()
        self.root.title("Family Asset Recovery and Verification System (FARVS)")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Icon setting disabled for now
        # self._set_window_icon()
        
        logger.debug("Root window created")
        
        # Database connection status
        self.db_connected = False
        self.db_error: Optional[str] = None
        
        # Current user
        self.current_user = get_current_user()
        logger.debug(f"Current user: {self.current_user.get('Username') if self.current_user else 'None'}")
        
        # Apply blue and white theme
        set_theme(self.root, get_env('APP_THEME', 'light'))
        logger.debug("Theme applied")
        
        # Initialize models
        self.users_model = UsersModel()
        logger.debug("Models initialized")
        
        # Setup UI
        self._setup_ui()
        logger.debug("UI setup complete")
        self._check_database_connection()
        logger.info(f"Database connection: {'Connected' if self.db_connected else 'Failed'}")
        
        # Show login if not authenticated
        if not self.current_user:
            logger.info("No user authenticated, showing login screen")
            self._show_login_screen()
        else:
            logger.info("User authenticated, showing main interface")
            self._show_main_interface()
    
    def _setup_ui(self):
        """Create the main UI structure."""
        # Configure root grid
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main container (will be replaced by login or main interface)
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
    
    def _show_login_screen(self):
        """Display integrated login form in main window."""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create login frame with centered layout
        login_frame = ttk.Frame(self.main_container, padding="40")
        login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        login_frame.columnconfigure(0, weight=1)
        
        # Center the login form
        center_frame = ttk.Frame(login_frame)
        center_frame.grid(row=0, column=0)
        
        # Title
        title_label = ttk.Label(
            center_frame,
            text="FARVS",
            font=("Segoe UI", 32, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            center_frame,
            text="Family Asset Recovery and Verification System",
            font=("Segoe UI", 12)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 40))
        
        # Login form frame
        form_frame = ttk.LabelFrame(center_frame, text="Sign In", padding="30")
        form_frame.grid(row=2, column=0, pady=20)
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=30, font=("Segoe UI", 10))
        username_entry.grid(row=1, column=0, pady=(0, 15), ipady=5)
        username_entry.focus()
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, width=30, show="*", font=("Segoe UI", 10))
        password_entry.grid(row=3, column=0, pady=(0, 20), ipady=5)
        
        # Bind Enter key to login
        username_entry.bind('<Return>', lambda e: self._signin())
        password_entry.bind('<Return>', lambda e: self._signin())
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, pady=(0, 10))
        
        # Sign in button
        signin_btn = ttk.Button(
            buttons_frame,
            text="Sign In",
            command=self._signin,
            width=15
        )
        signin_btn.grid(row=0, column=0, padx=5)
        
        # Create user/account button (only show if no users exist or if admin is logged in)
        # For initial setup, allow account creation. After that, only admins can create users.
        self.create_user_btn = ttk.Button(
            buttons_frame,
            text="Create Account",  # Will be updated based on context
            command=self._create_user,
            width=15
        )
        self.create_user_btn.grid(row=0, column=1, padx=5)
        
        # Check if users exist and update button visibility/text
        self._update_create_user_button_visibility()
        
        # Database status (if not connected)
        if not self.db_connected:
            status_label = ttk.Label(
                center_frame,
                text="⚠ Database not connected. Some features may be unavailable.",
                foreground="orange",
                font=("Segoe UI", 9)
            )
            status_label.grid(row=3, column=0, pady=(20, 0))
    
    def _show_main_interface(self):
        """Display main application interface with sidebar and tabs."""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area (this creates the notebook)
        self._create_main_content()
        
        # Update sidebar navigation after notebook is created
        self._update_sidebar_navigation()
        
        # Create menu bar
        self._create_menu()
    
    def _create_sidebar(self):
        """Create sidebar navigation for crucial parts."""
        # Sidebar frame
        sidebar = tk.Frame(self.root, bg="#1E3A8A", width=250)
        sidebar.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        sidebar.grid_propagate(False)
        self.root.columnconfigure(0, minsize=250)
        
        # Sidebar content
        sidebar_content = tk.Frame(sidebar, bg="#1E3A8A")
        sidebar_content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Logo/Title
        logo_frame = tk.Frame(sidebar_content, bg="#1E3A8A", height=80)
        logo_frame.pack(fill=tk.X, pady=(0, 20))
        logo_frame.pack_propagate(False)
        
        title_label = tk.Label(
            logo_frame,
            text="FARVS",
            font=("Segoe UI", 24, "bold"),
            bg="#1E3A8A",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", 0, "#3B82F6"),
            ("👤 Deceased", 1, "#2563EB"),
            ("💰 Assets", 2, "#2563EB"),
            ("📋 Claims", 3, "#2563EB"),
            ("📈 Reports", 4, "#2563EB"),
        ]
        
        # Add User Management for admins only
        current_user = get_current_user()
        if current_user and current_user.get("Role") == "Admin":
            nav_items.append(("👥 User Management", 5, "#2563EB"))
        
        self.nav_buttons = []
        for text, tab_index, color in nav_items:
            btn = tk.Button(
                sidebar_content,
                text=text,
                font=("Segoe UI", 11, "bold"),
                bg="#1E3A8A",
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief=tk.FLAT,
                anchor=tk.W,
                padx=20,
                pady=15,
                command=lambda idx=tab_index: self._navigate_to_tab(idx),
                cursor="hand2"
            )
            btn.pack(fill=tk.X, padx=0, pady=2)
            self.nav_buttons.append(btn)
        
        # Spacer
        spacer = tk.Frame(sidebar_content, bg="#1E3A8A", height=20)
        spacer.pack(fill=tk.X)
        
        # Profile/Settings section
        profile_frame = tk.Frame(sidebar_content, bg="#1E3A8A")
        profile_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        
        # User info
        if self.current_user:
            user_label = tk.Label(
                profile_frame,
                text=f"👤 {self.current_user.get('Username', 'User')}",
                font=("Segoe UI", 10),
                bg="#1E3A8A",
                fg="white"
            )
            user_label.pack(pady=(0, 5))
            
            role_label = tk.Label(
                profile_frame,
                text=f"Role: {self.current_user.get('Role', 'User')}",
                font=("Segoe UI", 9),
                bg="#1E3A8A",
                fg="#DBEAFE"
            )
            role_label.pack(pady=(0, 10))
        
        # Profile/Settings button
        profile_btn = tk.Button(
            profile_frame,
            text="⚙️ Profile & Settings",
            font=("Segoe UI", 10, "bold"),
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=10,
            command=self._show_profile_settings,
            cursor="hand2"
        )
        profile_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Logout button
        logout_btn = tk.Button(
            profile_frame,
            text="🚪 Logout",
            font=("Segoe UI", 10),
            bg="#EF4444",
            fg="white",
            activebackground="#DC2626",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._logout,
            cursor="hand2"
        )
        logout_btn.pack(fill=tk.X)
    
    def _create_main_content(self):
        """Create main content area with header and tabs."""
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Header bar
        header_frame = ttk.Frame(content_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Family Asset Recovery and Verification System",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Right side: Database status
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Database status
        if self.db_connected:
            status_text = "✓ Connected"
            status_color = "green"
        else:
            status_text = f"✗ {self.db_error[:30] if self.db_error else 'Not connected'}"
            status_color = "red"
        
        status_label = ttk.Label(
            right_frame,
            text=status_text,
            foreground=status_color,
            font=("Segoe UI", 9)
        )
        status_label.grid(row=0, column=0, padx=(0, 15))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        content_frame.rowconfigure(1, weight=1)
        
        # Dashboard tab
        self._create_dashboard_tab()
        
        # Deceased Records tab
        self._create_deceased_tab()
        
        # Assets tab
        self._create_assets_tab()
        
        # Claims tab
        self._create_claims_tab()
        
        # Reports tab
        self._create_reports_tab()
        
        # User Management tab (admin only)
        current_user = get_current_user()
        if current_user and current_user.get("Role") == "Admin":
            self._create_users_tab()
    
    def _navigate_to_tab(self, tab_index: int):
        """Navigate to a specific tab with error handling."""
        try:
            if hasattr(self, 'notebook') and self.notebook:
                # Check if tab exists
                num_tabs = self.notebook.index('end')
                if 0 <= tab_index < num_tabs:
                    self.notebook.select(tab_index)
                else:
                    print(f"Warning: Tab index {tab_index} out of bounds (total tabs: {num_tabs})")
        except Exception as e:
            print(f"Error navigating to tab {tab_index}: {e}")
    
    def _update_sidebar_navigation(self):
        """Update sidebar button states based on current tab."""
        try:
            if hasattr(self, 'notebook') and self.notebook:
                current_tab = self.notebook.index(self.notebook.select())
                for i, btn in enumerate(self.nav_buttons):
                    if i == current_tab:
                        btn.config(bg="#3B82F6")  # Active color
                    else:
                        btn.config(bg="#1E3A8A")  # Default color
        except Exception:
            pass  # Non-critical
    
    def _show_profile_settings(self):
        """Show profile and settings dialog."""
        from ui.components import ModalDialog
        
        modal = ModalDialog(self.root, "Profile & Settings", width=600, height=500)
        
        # Content frame
        content = ttk.Frame(modal.content_frame, padding="20")
        content.pack(fill=tk.BOTH, expand=True)
        
        # User Information Section
        user_frame = ttk.LabelFrame(content, text="User Information", padding="15")
        user_frame.pack(fill=tk.X, pady=(0, 15))
        
        if self.current_user:
            ttk.Label(user_frame, text=f"Username: {self.current_user.get('Username', 'N/A')}", 
                     font=("Segoe UI", 10)).pack(anchor=tk.W, pady=5)
            ttk.Label(user_frame, text=f"Role: {self.current_user.get('Role', 'N/A')}", 
                     font=("Segoe UI", 10)).pack(anchor=tk.W, pady=5)
            ttk.Label(user_frame, text=f"User ID: {self.current_user.get('UserId', 'N/A')}", 
                     font=("Segoe UI", 10)).pack(anchor=tk.W, pady=5)
        
        # Application Settings Section
        settings_frame = ttk.LabelFrame(content, text="Application Settings", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Database connection info
        db_info_frame = ttk.Frame(settings_frame)
        db_info_frame.pack(fill=tk.X, pady=5)
        ttk.Label(db_info_frame, text="Database Server:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Label(db_info_frame, text=get_env('DB_SERVER', 'Not configured'), 
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        db_info_frame2 = ttk.Frame(settings_frame)
        db_info_frame2.pack(fill=tk.X, pady=5)
        ttk.Label(db_info_frame2, text="Database Name:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Label(db_info_frame2, text=get_env('DB_NAME', 'Not configured'), 
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Connection status
        status_frame = ttk.Frame(settings_frame)
        status_frame.pack(fill=tk.X, pady=10)
        if self.db_connected:
            status_text = "✓ Database Connected"
            status_color = "green"
        else:
            status_text = f"✗ Database Error: {self.db_error[:50] if self.db_error else 'Not connected'}"
            status_color = "red"
        ttk.Label(status_frame, text=status_text, foreground=status_color, 
                 font=("Segoe UI", 9, "bold")).pack()
        
        # Test connection button
        test_btn = ttk.Button(
            settings_frame,
            text="Test Database Connection",
            command=lambda: self._test_connection(modal)
        )
        test_btn.pack(pady=10)
        
        # Buttons
        modal.add_button("Close", style="default")
        
        modal.show()
    
    def _test_connection(self, modal):
        """Test database connection from settings."""
        self._check_database_connection()
        if self.db_connected:
            messagebox.showinfo("Success", "Database connection successful!")
        else:
            messagebox.showerror("Error", f"Database connection failed: {self.db_error}")
    
    def _create_dashboard_tab(self):
        """Create dashboard tab with modern card-based layout."""
        dashboard_frame = ttk.Frame(self.notebook, padding="20")
        dashboard_frame.configure(style="TFrame")
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Configure grid
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.columnconfigure(1, weight=1)
        
        # Load statistics
        try:
            from db.models_deceased import DeceasedModel
            from db.models_assets import AssetsModel
            from db.models_claims import ClaimsModel
            
            deceased_model = DeceasedModel()
            assets_model = AssetsModel()
            claims_model = ClaimsModel()
            
            deceased_count = deceased_model.count()
            assets_count = assets_model.count()
            claims_count = claims_model.count()
            pending_count = claims_model.count_by_status('Pending')
            verified_count = claims_model.count_by_status('Verified')
            settled_count = claims_model.count_by_status('Settled')
        except Exception:
            deceased_count = 0
            assets_count = 0
            claims_count = 0
            pending_count = 0
            verified_count = 0
            settled_count = 0
        
        # Statistics Cards - Row 1
        stats_row1 = ttk.Frame(dashboard_frame)
        stats_row1.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_row1.columnconfigure(0, weight=1)
        stats_row1.columnconfigure(1, weight=1)
        stats_row1.columnconfigure(2, weight=1)
        stats_row1.columnconfigure(3, weight=1)
        
        # Card 1: Deceased Records
        self._create_stat_card(
            stats_row1, 0, 0,
            icon="👤",
            title="Deceased Records",
            value=str(deceased_count),
            color="#1E3A8A",
            subtitle="Total records"
        )
        
        # Card 2: Total Assets
        self._create_stat_card(
            stats_row1, 0, 1,
            icon="💰",
            title="Total Assets",
            value=str(assets_count),
            color="#3B82F6",
            subtitle="Assets tracked"
        )
        
        # Card 3: Total Claims
        self._create_stat_card(
            stats_row1, 0, 2,
            icon="📋",
            title="Total Claims",
            value=str(claims_count),
            color="#2563EB",
            subtitle="All claims"
        )
        
        # Card 4: Pending Claims
        self._create_stat_card(
            stats_row1, 0, 3,
            icon="⏳",
            title="Pending Claims",
            value=str(pending_count),
            color="#F59E0B",
            subtitle="Requires attention"
        )
        
        # Claims Status Cards - Row 2
        claims_row = ttk.Frame(dashboard_frame)
        claims_row.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        claims_row.columnconfigure(0, weight=1)
        claims_row.columnconfigure(1, weight=1)
        claims_row.columnconfigure(2, weight=1)
        
        # Verified Claims Card
        self._create_stat_card(
            claims_row, 0, 0,
            icon="✅",
            title="Verified",
            value=str(verified_count),
            color="#10B981",
            subtitle="Verified claims"
        )
        
        # Settled Claims Card
        self._create_stat_card(
            claims_row, 0, 1,
            icon="✔️",
            title="Settled",
            value=str(settled_count),
            color="#059669",
            subtitle="Completed claims"
        )
        
        # Quick Actions Card
        actions_card = tk.Frame(
            dashboard_frame,
            bg="#F8FAFC",
            relief="solid",
            borderwidth=1,
            bd=1
        )
        actions_card.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        actions_card.columnconfigure(0, weight=1)
        actions_card.columnconfigure(1, weight=1)
        actions_card.columnconfigure(2, weight=1)
        actions_card.columnconfigure(3, weight=1)
        
        # Card header
        header_frame = tk.Frame(actions_card, bg="#F8FAFC")
        header_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=15, pady=(15, 10))
        ttk.Label(
            header_frame,
            text="⚡ Quick Actions",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
            background="#F8FAFC"
        ).pack(side=tk.LEFT)
        
        # Action buttons
        actions = [
            ("➕ Add Deceased", lambda: self.notebook.select(1), "👤"),
            ("➕ Add Asset", lambda: self.notebook.select(2), "💰"),
            ("📝 Process Claims", lambda: self.notebook.select(3), "📋"),
            ("📊 View Reports", lambda: self.notebook.select(4), "📈")
        ]
        
        for i, (text, command, icon) in enumerate(actions):
            btn_frame = tk.Frame(actions_card, bg="#F8FAFC")
            btn_frame.grid(row=1, column=i, padx=10, pady=(0, 15), sticky=(tk.W, tk.E))
            
            btn = ttk.Button(
                btn_frame,
                text=f"{icon} {text}",
                command=command,
                width=20
            )
            btn.pack(padx=5)
        
        # Recent Activity Section
        activity_card = tk.Frame(
            dashboard_frame,
            bg="#F8FAFC",
            relief="solid",
            borderwidth=1,
            bd=1
        )
        activity_card.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        activity_card.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(3, weight=1)
        
        # Activity header
        activity_header = tk.Frame(activity_card, bg="#F8FAFC")
        activity_header.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=15, pady=15)
        ttk.Label(
            activity_header,
            text="📋 Recent Activity",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
            background="#F8FAFC"
        ).pack(side=tk.LEFT)
        
        # Activity content
        activity_content = ttk.Frame(activity_card, padding="15")
        activity_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        activity_card.rowconfigure(1, weight=1)
        
        try:
            from db.models_claims import ClaimsModel
            claims_model = ClaimsModel()
            recent_claims = claims_model.get_all_with_details()[:5]
            
            if recent_claims:
                for i, claim in enumerate(recent_claims):
                    claim_frame = ttk.Frame(activity_content)
                    claim_frame.pack(fill=tk.X, pady=5)
                    
                    # Status badge
                    from ui.components import StatusBadge
                    StatusBadge.create(claim_frame, claim.get('Status', 'Pending'), row=0, column=0)
                    
                    # Claim info
                    info_text = f"Claim #{claim.get('ClaimId', 'N/A')} - {claim.get('AssetType', 'Asset')}"
                    ttk.Label(
                        claim_frame,
                        text=info_text,
                        font=("Segoe UI", 9)
                    ).grid(row=0, column=1, padx=10, sticky=tk.W)
                    
                    # Date
                    created = claim.get('CreatedAt', '')
                    if created:
                        date_text = str(created)[:10] if len(str(created)) > 10 else str(created)
                        ttk.Label(
                            claim_frame,
                            text=date_text,
                            font=("Segoe UI", 8),
                            foreground="#6B7280"
                        ).grid(row=0, column=2, sticky=tk.E)
            else:
                from ui.components import EmptyState
                EmptyState.show(
                    activity_content,
                    "No recent activity",
                    "View Claims",
                    lambda: self.notebook.select(3)
                )
        except Exception:
            ttk.Label(
                activity_content,
                text="Unable to load recent activity",
                foreground="#6B7280"
            ).pack()
    
    def _create_stat_card(self, parent: ttk.Frame, row: int, column: int,
                         icon: str, title: str, value: str, color: str, subtitle: str = ""):
        """
        Create a modern stat card.
        
        Args:
            parent: Parent frame
            row: Grid row
            column: Grid column
            icon: Icon/emoji
            title: Card title
            value: Stat value
            color: Accent color
            subtitle: Optional subtitle
        """
        # Card frame with shadow effect
        card = tk.Frame(
            parent,
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            bd=1
        )
        card.grid(row=row, column=column, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        card.columnconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        
        # Card content
        content = tk.Frame(card, bg="#FFFFFF", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        
        # Icon and title row
        header = tk.Frame(content, bg="#FFFFFF")
        header.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = ttk.Label(
            header,
            text=icon,
            font=("Segoe UI", 24),
            background="#FFFFFF"
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = tk.Frame(header, bg="#FFFFFF")
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            foreground="#1F2937",
            background="#FFFFFF"
        )
        title_label.pack(anchor=tk.W)
        
        if subtitle:
            subtitle_label = ttk.Label(
                title_frame,
                text=subtitle,
                font=("Segoe UI", 9),
                foreground="#6B7280",
                background="#FFFFFF"
            )
            subtitle_label.pack(anchor=tk.W)
        
        # Value
        value_label = ttk.Label(
            content,
            text=value,
            font=("Segoe UI", 32, "bold"),
            foreground=color,
            background="#FFFFFF"
        )
        value_label.pack(anchor=tk.W)
    
    def _create_deceased_tab(self):
        """Create deceased records tab."""
        deceased_frame = ttk.Frame(self.notebook)
        deceased_frame.columnconfigure(0, weight=1)
        deceased_frame.rowconfigure(0, weight=1)
        self.notebook.add(deceased_frame, text="👤 Deceased Records")
        
        # Import and create deceased window content in the frame
        try:
            from ui.ui_deceased import DeceasedWindow
            self.deceased_window = DeceasedWindow(self.root, container=deceased_frame)
        except Exception as e:
            error_label = ttk.Label(
                deceased_frame,
                text=f"Error loading Deceased module: {e}",
                foreground="red"
            )
            error_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
    
    def _create_assets_tab(self):
        """Create assets management tab."""
        assets_frame = ttk.Frame(self.notebook)
        assets_frame.columnconfigure(0, weight=1)
        assets_frame.rowconfigure(0, weight=1)
        self.notebook.add(assets_frame, text="💰 Assets")
        
        try:
            from ui.ui_assets import AssetsWindow
            self.assets_window = AssetsWindow(self.root, container=assets_frame)
        except Exception as e:
            error_label = ttk.Label(
                assets_frame,
                text=f"Error loading Assets module: {e}",
                foreground="red"
            )
            error_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
    
    def _create_claims_tab(self):
        """Create claims processing tab."""
        claims_frame = ttk.Frame(self.notebook)
        claims_frame.columnconfigure(0, weight=1)
        claims_frame.rowconfigure(0, weight=1)
        self.notebook.add(claims_frame, text="📋 Claims")
        
        try:
            from ui.ui_claims import ClaimsWindow
            self.claims_window = ClaimsWindow(self.root, container=claims_frame)
        except Exception as e:
            import traceback
            error_text = f"Error loading Claims module:\n{str(e)}\n\n{traceback.format_exc()}"
            error_label = ttk.Label(
                claims_frame,
                text=error_text,
                foreground="red",
                wraplength=600
            )
            error_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
    
    def _create_reports_tab(self):
        """Create reports tab."""
        reports_frame = ttk.Frame(self.notebook)
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.rowconfigure(0, weight=1)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        try:
            from ui.ui_reports import ReportsWindow
            self.reports_window = ReportsWindow(self.root, container=reports_frame)
        except Exception as e:
            error_label = ttk.Label(
                reports_frame,
                text=f"Error loading Reports module: {e}",
                foreground="red"
            )
            error_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
    
    def _create_users_tab(self):
        """Create the User Management tab (admin only)."""
        users_frame = ttk.Frame(self.notebook)
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(0, weight=1)
        self.notebook.add(users_frame, text="👥 User Management")
        
        try:
            from ui.ui_users import UsersWindow
            self.users_window = UsersWindow(container=users_frame)
        except Exception as e:
            error_label = ttk.Label(
                users_frame,
                text=f"Error loading User Management module: {e}",
                foreground="red"
            )
            error_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Dashboard", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Deceased Records", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Assets", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="Claims", command=lambda: self.notebook.select(3))
        view_menu.add_command(label="Reports", command=lambda: self.notebook.select(4))
        
        # Session menu
        session_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Session", menu=session_menu)
        session_menu.add_command(label="Profile & Settings", command=self._show_profile_settings)
        session_menu.add_command(label="Logout", command=self._logout)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About FARVS", command=self._show_about)
    
    def _check_database_connection(self):
        """Test database connectivity and update status display."""
        try:
            self.db_connected, self.db_error = try_connect()
        except Exception as e:
            self.db_connected = False
            self.db_error = str(e)
    
    def _signin(self):
        """Handle user sign in with secure password verification."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        logger.info(f"Login attempt for username: {username}")
        
        if not username:
            logger.warning("Login failed: Username is required")
            messagebox.showerror("Authentication", "Username is required")
            return
        
        if not password:
            logger.warning("Login failed: Password is required")
            messagebox.showerror("Authentication", "Password is required")
            return
        
        try:
            logger.debug(f"Fetching user from database: {username}")
            user = self.users_model.get_by_username(username)
            if not user:
                logger.warning(f"Login failed: User not found - {username}")
                messagebox.showerror("Authentication", "Invalid username or password")
                return
            
            logger.debug(f"User found: ID={user['UserId']}, Role={user['Role']}")
            
            # Secure password verification
            stored_hash = user["PasswordHash"]
            if not stored_hash:
                logger.warning(f"Login failed: No password hash for user {username}")
                messagebox.showerror("Authentication", "Invalid username or password")
                return
            
            logger.debug(f"Password hash type: {type(stored_hash)}, length: {len(stored_hash) if isinstance(stored_hash, bytes) else 'N/A'}")
            
            # Try new secure hash format first (64 bytes: salt + hash)
            if isinstance(stored_hash, bytes) and len(stored_hash) == 64:
                logger.debug("Using secure hash verification (SHA-256 with salt)")
                if not verify_password(password, stored_hash):
                    logger.warning(f"Login failed: Password verification failed for {username}")
                    messagebox.showerror("Authentication", "Invalid username or password")
                    return
            else:
                # Legacy password format (plain bytes) - for backward compatibility
                logger.debug("Using legacy password verification")
                legacy_hash = hash_password_legacy(password)
                logger.debug(f"Legacy hash length: {len(legacy_hash)}, Stored hash length: {len(stored_hash) if isinstance(stored_hash, bytes) else 'N/A'}")
                
                if isinstance(stored_hash, bytes):
                    if not secrets.compare_digest(legacy_hash, stored_hash):
                        logger.warning(f"Login failed: Legacy password verification failed for {username}")
                        messagebox.showerror("Authentication", "Invalid username or password")
                        return
                    else:
                        logger.debug("Legacy password verification successful")
                else:
                    # String comparison for very old data
                    if password != str(stored_hash):
                        logger.warning(f"Login failed: String password comparison failed for {username}")
                        messagebox.showerror("Authentication", "Invalid username or password")
                        return
                    else:
                        logger.debug("String password comparison successful")
        
            logger.info(f"Password verified successfully for {username}")
            
            # Update last login time
            try:
                from db.db_connect import get_connection
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE Users SET LastLoginAt = SYSUTCDATETIME() WHERE UserId = ?",
                        (user["UserId"],)
                    )
                    conn.commit()
                logger.debug(f"Last login time updated for user {username}")
            except Exception as e:
                logger.warning(f"Failed to update last login time: {e}")
                pass  # Non-critical, continue with login
            
            # Set current user
            try:
                logger.debug(f"Setting current user: {user['Username']} (ID: {user['UserId']}, Role: {user['Role']})")
                set_current_user({
                    "UserId": user["UserId"],
                    "Username": user["Username"],
                    "Role": user["Role"]
                })
                self.current_user = get_current_user()
                logger.debug(f"Current user set successfully: {self.current_user}")
            except Exception as e:
                logger.error(f"Failed to set current user: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to set user session: {str(e)}")
                return
            
            logger.info(f"Login successful for {username} (Role: {user['Role']})")
            
            # Switch to main interface
            try:
                logger.debug("Calling _show_main_interface()")
                self._show_main_interface()
                logger.debug("Main interface shown successfully")
            except Exception as e:
                logger.error(f"Failed to show main interface: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to load main interface: {str(e)}")
            
        except Exception as e:
            logger.error(f"Login exception: {e}", exc_info=True)
            messagebox.showerror("Authentication", f"Login failed: {str(e)}")
    
    def _update_create_user_button_visibility(self):
        """Update visibility and text of Create Account button based on user role and existing users."""
        try:
            all_users = self.users_model.list()
            current_user = get_current_user()
            
            if not hasattr(self, 'create_user_btn'):
                return
            
            # Show button if:
            # 1. No users exist (initial setup - first-time onboarding)
            # 2. Current user is Admin (logged in as admin)
            if not all_users:
                # Initial setup - show "Create Account" button
                self.create_user_btn.config(text="Create Account")
                self.create_user_btn.grid()
            elif current_user and current_user.get('Role') == 'Admin':
                # Admin is logged in - show "Create User" button
                self.create_user_btn.config(text="Create User")
                self.create_user_btn.grid()
            else:
                # Non-admin or not logged in - hide button
                self.create_user_btn.grid_remove()
        except Exception:
            # If check fails, show button (safer default for initial setup)
            if hasattr(self, 'create_user_btn'):
                self.create_user_btn.config(text="Create Account")
                self.create_user_btn.grid()
    
    def _create_user(self):
        """Handle user creation - only allowed for Admin users or if no users exist (first-time setup)."""
        from db.models_users import UsersModel
        
        # Check if any users exist
        users_model = UsersModel()
        all_users = users_model.list()
        is_first_user = not all_users
        
        # If users exist, check if current user is admin
        if all_users and self.current_user:
            if self.current_user.get('Role') != 'Admin':
                messagebox.showerror("Access Denied", "Only administrators can create new users.")
                return
        elif all_users and not self.current_user:
            # User is not logged in but users exist - need admin login
            messagebox.showerror("Access Denied", "Only administrators can create new users. Please log in as an admin first.")
            return
        
        # Show user creation dialog
        from ui.components import ModalDialog
        
        # Different title and messaging for first-time setup
        if is_first_user:
            modal_title = "Create Admin Account"
            info_text = "Welcome! Create the first administrator account for your organization.\nThis account will have full administrative privileges."
        else:
            modal_title = "Create New User"
            info_text = "Create a new user account. Only administrators can create users."
        
        modal = ModalDialog(self.root, modal_title, width=500, height=450)
        
        # Form fields
        form_frame = ttk.Frame(modal.content_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        info_label = ttk.Label(
            form_frame, 
            text=info_text, 
            font=("Segoe UI", 9),
            foreground="gray",
            wraplength=400,
            justify=tk.LEFT
        )
        info_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        
        # Username
        ttk.Label(form_frame, text="Username:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=username_var, width=30, font=("Segoe UI", 10))
        username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        username_entry.focus()
        
        # Password
        ttk.Label(form_frame, text="Password:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=password_var, width=30, show="*", font=("Segoe UI", 10))
        password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Role (first user gets Admin automatically, others can be set by admin)
        role_label = ttk.Label(form_frame, text="Role:", font=("Segoe UI", 10))
        role_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        role_var = tk.StringVar()
        
        if is_first_user:
            # First user is automatically Admin - show as read-only
            role_var.set("Admin")
            role_display = ttk.Label(
                form_frame, 
                text="Admin (First account)", 
                font=("Segoe UI", 10, "bold"),
                foreground="green"
            )
            role_display.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        else:
            # Admin can set role for new users
            role_var.set("Staff")
            role_combo = ttk.Combobox(form_frame, textvariable=role_var, width=27, state="readonly")
            role_combo['values'] = ('Admin', 'Staff', 'Viewer')
            role_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Error label
        error_label = ttk.Label(form_frame, text="", foreground="red", font=("Segoe UI", 9))
        error_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        def save_user():
            """Save user from modal."""
            username = username_var.get().strip()
            password = password_var.get()
            
            # Validate
            if not username:
                error_label.config(text="Username is required")
                return
            if not password:
                error_label.config(text="Password is required")
                return
            if len(password) < 3:
                error_label.config(text="Password must be at least 3 characters")
                return
            
            try:
                # Determine role: Admin for first user, selected role for others
                if is_first_user:
                    role = "Admin"  # First user is always Admin
                else:
                    role = role_var.get()
                
                # Use secure password hashing
                password_hash = hash_password(password)
                
                # For first user, use simple create (no admin required)
                # For subsequent users, use stored procedure (requires admin)
                if is_first_user:
                    user_id = users_model.create(
                        username=username,
                        password_hash=password_hash,
                        role=role
                    )
                else:
                    # Use stored procedure for subsequent users (requires admin)
                    from db.db_operations import db_ops
                    success, user_id, error = db_ops.create_user_by_admin(
                        username=username,
                        password_hash=password_hash,
                        role=role,
                        created_by_user_id=self.current_user["UserId"],
                        create_sql_login=True
                    )
                    if not success:
                        error_label.config(text=error or "Failed to create user")
                        return
                
                modal.result = True
                modal.dialog.destroy()
                
                if is_first_user:
                    messagebox.showinfo(
                        "Account Created", 
                        f"Admin account '{username}' created successfully!\n\n"
                        "You will now be logged in automatically."
                    )
                else:
                    messagebox.showinfo("Success", f"User '{username}' created successfully with role '{role}'.")
                
                # If no user was logged in (first-time setup), log in as the new user
                if not self.current_user:
                    set_current_user({
                        "UserId": user_id,
                        "Username": username,
                        "Role": role
                    })
                    self.current_user = get_current_user()
                    self._show_main_interface()
                else:
                    # Update button visibility after user creation
                    self._update_create_user_button_visibility()
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE" in error_msg or "duplicate" in error_msg.lower() or "already exists" in error_msg.lower():
                    error_label.config(text="Username already exists")
                else:
                    error_label.config(text=f"Error: {error_msg}")
                logger.error(f"Error creating user: {e}", exc_info=True)
        
        # Bind Enter key
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: save_user())
        
        # Buttons
        modal.add_button("Cancel", style="default")
        if is_first_user:
            modal.add_button("Create Admin Account", save_user, style="primary")
        else:
            modal.add_button("Create User", save_user, style="primary")
        
        # Show modal
        modal.show()
    
    # Icon setting disabled - can be re-enabled later if needed
    # def _set_window_icon(self):
    #     """Set the taskbar/window icon using Windows API."""
    #     pass
    
    def _logout(self):
        """Handle user logout."""
        # Clear user session
        set_current_user(None)
        self.current_user = None
        
        # Clear all widgets from root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate main container
        self._setup_ui()
        
        # Show login screen
        self._show_login_screen()
    
    def _show_about(self):
        """Display application information dialog."""
        about_text = """
Family Asset Recovery and Verification System (FARVS)

Version: 1.0.0
Database: Microsoft SQL Server
Interface: Python Tkinter

This system enables families to trace, verify, and claim 
unclaimed assets of deceased relatives through a comprehensive 
database management interface.

Developed for Database Systems Group Project
        """
        messagebox.showinfo("About FARVS", about_text.strip())
    
    def run(self):
        """Start the main application event loop."""
        self.root.mainloop()


def main():
    """
    Application entry point.
    
    Initializes the main window and starts the Tkinter event loop.
    Handles any startup errors gracefully.
    """
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Fatal error starting FARVS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
