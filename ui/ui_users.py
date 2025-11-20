"""
FARVS User Management Module
=============================

This module provides user management functionality for administrators.
Only admins can access this module to add, edit, and delete users.

Features:
- Add new users (admin only)
- Edit user roles and permissions
- Delete users
- View all users
- Search and filter users
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any

# Import database operations and authentication
from db.db_operations import db_ops
from auth.session import get_current_user
from auth.password import hash_password
from ui.theme import stripe_treeview
import logging

logger = logging.getLogger(__name__)


class UsersWindow:
    """
    Tkinter window for managing users (admin only).
    
    Features:
    - Add new users
    - Edit user roles
    - Delete users
    - Search and filter users
    """
    
    def __init__(self, parent=None, container=None):
        """
        Initialize the Users Management window.
        
        Args:
            parent: Parent window (if standalone)
            container: Container frame (if embedded in tabs)
        """
        self.parent = parent
        self.container = container
        self.window = container if container else tk.Toplevel(parent) if parent else tk.Tk()
        
        # Database operations (using stored procedures with SQL Server login support)
        
        # Current selection
        self.current_user = None
        self.users = []
        
        # Setup UI
        self._setup_ui()
        self._load_users()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - User form
        form_frame = ttk.LabelFrame(main_frame, text="User Information", padding="10")
        form_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        
        # Form fields container - Use ScrollableFrame for scrolling support
        from ui.scrollable_frame import ScrollableFrame
        form_fields_container = ScrollableFrame(form_frame)
        form_fields_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Create form fields in the inner_frame of ScrollableFrame
        self._create_form_fields(form_fields_container.inner_frame)
        
        # Right panel - Users list
        list_frame = ttk.LabelFrame(main_frame, text="Users List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        # CRITICAL: Configure list_frame for proper expansion
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Search
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Role filter
        ttk.Label(search_frame, text="Role:").grid(row=0, column=2, padx=(0, 5))
        self.role_filter_var = tk.StringVar()
        role_combo = ttk.Combobox(search_frame, textvariable=self.role_filter_var, width=15, state="readonly")
        role_combo['values'] = ('All', 'Admin', 'Staff', 'Viewer')
        role_combo.set('All')
        role_combo.bind('<<ComboboxSelected>>', self._on_role_filter_change)
        role_combo.grid(row=0, column=3)
        
        # Users treeview container - CRITICAL: Must have proper grid weights
        users_container = ttk.Frame(list_frame)
        users_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        users_container.columnconfigure(0, weight=1)
        users_container.rowconfigure(0, weight=1)
        self._create_users_treeview(users_container)
        
        # Bottom panel - Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._create_action_buttons(actions_frame)
    
    def _create_form_fields(self, parent: ttk.Frame):
        """Create form input fields for user data."""
        from ui.components import create_tooltip
        
        # Username (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Username:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(parent, textvariable=self.username_var, width=25)
        username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(username_entry, "Required: Unique username for login")
        
        # Password (Required for new users)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Password:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(parent, textvariable=self.password_var, width=25, show="*")
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(password_entry, "Required: Password (leave blank to keep existing)")
        
        # Role (Required)
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(label_frame, text="Role:").pack(side=tk.LEFT)
        ttk.Label(label_frame, text="*", foreground="red").pack(side=tk.LEFT, padx=(2, 0))
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(parent, textvariable=self.role_var, width=22, state="readonly")
        role_combo['values'] = ('Admin', 'Staff', 'Viewer')
        role_combo.set('Staff')
        role_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(role_combo, "Required: User role (Admin or User)")
        
        # User ID (read-only, for editing)
        ttk.Label(parent, text="User ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        user_id_entry = ttk.Entry(parent, textvariable=self.user_id_var, width=25, state="readonly")
        user_id_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        create_tooltip(user_id_entry, "User ID (auto-generated)")
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def _create_users_treeview(self, parent: ttk.Frame):
        """Create the treeview widget for displaying users."""
        # Treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights - CRITICAL for scrolling
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview columns
        columns = ("ID", "Username", "Role", "Created At")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings and widths
        column_widths = {"ID": 50, "Username": 150, "Role": 100, "Created At": 150}
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
        self.tree.bind("<<TreeviewSelect>>", self._on_user_select)
    
    def _create_action_buttons(self, parent: ttk.Frame):
        """Create action buttons for CRUD operations."""
        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        ttk.Button(btn_frame, text="➕ Add User", command=self._add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Update User", command=self._update_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete User", command=self._delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self._load_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 Clear Form", command=self._clear_form).pack(side=tk.LEFT, padx=5)
    
    def _load_users(self):
        """Load users from database using stored procedure."""
        try:
            self.users = db_ops.get_all_users()
            self._display_users()
            logger.info(f"Loaded {len(self.users)} users from database")
        except Exception as e:
            error_msg = f"Failed to load users: {e}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _display_users(self):
        """Display users in treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate treeview
        for user in self.users:
            values = (
                user["UserId"],
                user["Username"],
                user["Role"],
                str(user.get("CreatedAt", ""))[:19] if user.get("CreatedAt") else ""
            )
            self.tree.insert("", tk.END, values=values)
        
        # Zebra striping
        stripe_treeview(self.tree)
    
    def _on_user_select(self, event):
        """Handle user selection in treeview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected user data
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        
        # Find user in data
        self.current_user = next((u for u in self.users if u["UserId"] == user_id), None)
        
        if self.current_user:
            self._populate_form(self.current_user)
    
    def _populate_form(self, user: Dict[str, Any]):
        """Populate form fields with user data."""
        self.user_id_var.set(str(user.get("UserId", "")))
        self.username_var.set(user.get("Username", ""))
        self.password_var.set("")  # Don't show password
        self.role_var.set(user.get("Role", "User"))
    
    def _on_search_change(self, *args):
        """Handle search text change to filter users."""
        search_text = self.search_var.get().lower()
        role_filter = self.role_filter_var.get()
        
        # Filter users
        filtered_users = [
            u for u in self.users
            if (search_text in str(u["UserId"]).lower() or
                search_text in u["Username"].lower() or
                search_text in u.get("Role", "").lower())
            and (role_filter == "All" or u.get("Role", "") == role_filter)
        ]
        
        # Clear and repopulate treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for user in filtered_users:
            values = (
                user["UserId"],
                user["Username"],
                user["Role"],
                str(user.get("CreatedAt", ""))[:19] if user.get("CreatedAt") else ""
            )
            self.tree.insert("", tk.END, values=values)
        
        stripe_treeview(self.tree)
    
    def _on_role_filter_change(self, event=None):
        """Handle role filter change."""
        self._on_search_change()
    
    def _validate_form(self) -> bool:
        """Validate form input data."""
        # Required fields
        if not self.username_var.get().strip():
            messagebox.showerror("Validation Error", "Username is required.")
            return False
        
        # Password required for new users
        if not self.current_user and not self.password_var.get().strip():
            messagebox.showerror("Validation Error", "Password is required for new users.")
            return False
        
        # Role required
        if not self.role_var.get().strip():
            messagebox.showerror("Validation Error", "Role is required.")
            return False
        
        return True
    
    def _add_user(self):
        """Add a new user with SQL Server login support."""
        if not self._validate_form():
            return
        
        try:
            # Get current user (must be admin)
            user = get_current_user()
            if not user:
                messagebox.showerror("Error", "You must be logged in to create users.")
                return
            
            created_by_user_id = user["UserId"]
            
            # Get form data
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            role = self.role_var.get().strip()
            email = None  # Email field not in form, can be added later
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create user using stored procedure (automatically creates SQL Server login)
            # SQL Server login password defaults to temp password, user should change it
            success, new_id, error = db_ops.create_user_by_admin(
                username=username,
                password_hash=hashed_password,
                role=role,
                created_by_user_id=created_by_user_id,
                email=email,
                create_sql_login=True  # Automatically create SQL Server login
            )
            
            if success:
                messagebox.showinfo("Success", 
                    f"User '{username}' created successfully.\n"
                    f"SQL Server login created with role: {role}\n"
                    f"Default SQL login password: TempPassword123!\n"
                    f"User should change this password on first login.")
                self._clear_form()
                self._load_users()
            else:
                messagebox.showerror("Error", f"Failed to add user: {error}")
            
        except Exception as e:
            error_msg = f"Failed to add user: {e}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _update_user(self):
        """Update the selected user record with SQL Server login permission updates."""
        if not self.current_user:
            messagebox.showwarning("No Selection", "Please select a user to update.")
            return
        
        if not self._validate_form():
            return
        
        try:
            # Get current user (must be admin)
            user = get_current_user()
            if not user:
                messagebox.showerror("Error", "You must be logged in to update users.")
                return
            
            updated_by_user_id = user["UserId"]
            
            # Get form data
            user_id = self.current_user["UserId"]
            username = self.username_var.get().strip()
            role = self.role_var.get().strip()
            email = None  # Email field not in form, can be added later
            
            # Update password only if provided
            password_hash = None
            password = self.password_var.get().strip()
            if password:
                password_hash = hash_password(password)
            
            # Update user using stored procedure (automatically updates SQL Server login permissions if role changes)
            success, error = db_ops.update_user_by_admin(
                user_id=user_id,
                updated_by_user_id=updated_by_user_id,
                username=username if username != self.current_user["Username"] else None,
                password_hash=password_hash,
                role=role if role != self.current_user["Role"] else None,
                email=email
            )
            
            if success:
                messagebox.showinfo("Success", 
                    f"User '{username}' updated successfully.\n"
                    + (f"SQL Server login permissions updated (role changed to: {role})." 
                       if role != self.current_user["Role"] else ""))
                self._load_users()
            else:
                messagebox.showerror("Error", f"Failed to update user: {error}")
            
        except Exception as e:
            error_msg = f"Failed to update user: {e}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _delete_user(self):
        """Delete the selected user record and associated SQL Server login."""
        if not self.current_user:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        
        # Get current user (must be admin)
        current_logged_user = get_current_user()
        if not current_logged_user:
            messagebox.showerror("Error", "You must be logged in to delete users.")
            return
        
        # Prevent deleting yourself (handled by stored procedure, but check here too)
        if current_logged_user["UserId"] == self.current_user["UserId"]:
            messagebox.showerror("Error", "You cannot delete your own account.")
            return
        
        # Confirmation dialog
        username = self.current_user["Username"]
        if not messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete user: {username}?\n\n"
            f"This will also delete the associated SQL Server login."):
            return
        
        try:
            # Delete user using stored procedure (automatically deletes SQL Server login)
            user_id = self.current_user["UserId"]
            deleted_by_user_id = current_logged_user["UserId"]
            
            success, error = db_ops.delete_user_by_admin(
                user_id=user_id,
                deleted_by_user_id=deleted_by_user_id
            )
            
            if success:
                messagebox.showinfo("Success", 
                    f"User '{username}' deleted successfully.\n"
                    f"SQL Server login has been removed.")
                self._clear_form()
                self._load_users()
            else:
                messagebox.showerror("Error", f"Failed to delete user: {error}")
            
        except Exception as e:
            error_msg = f"Failed to delete user: {e}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
    
    def _clear_form(self):
        """Clear all form fields."""
        self.user_id_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.role_var.set("Staff")
        
        self.current_user = None
        
        # Clear treeview selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)

