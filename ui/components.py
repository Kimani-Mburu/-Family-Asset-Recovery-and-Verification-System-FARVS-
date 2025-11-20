"""
Reusable UI Components for FARVS

This module provides reusable, industry-standard UI components including
modals, date pickers, status badges, and other common UI elements.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime, date
import calendar

from ui.theme import BLUE_PRIMARY, BLUE_SECONDARY, BLUE_LIGHT, WHITE, GRAY_TEXT, GRAY_LIGHT


class ModalDialog:
    """
    Reusable modal dialog component.
    
    Creates a centered modal dialog that blocks interaction with parent window
    until closed. Supports custom content and callbacks.
    """
    
    def __init__(self, parent: tk.Tk, title: str, width: int = 500, height: int = 400):
        """
        Initialize modal dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width in pixels
            height: Dialog height in pixels
        """
        self.parent = parent
        self.result = None
        self.callback = None
        
        # Create toplevel window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self._center_dialog()
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure style
        self.dialog.configure(bg=WHITE)
        
        # Main container
        self.container = ttk.Frame(self.dialog, padding="20")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.container,
            text=title,
            font=("Segoe UI", 14, "bold"),
            foreground=BLUE_PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Content frame (to be populated by subclasses)
        self.content_frame = ttk.Frame(self.container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.container)
        self.buttons_frame.pack(fill=tk.X, pady=(20, 0))
    
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def add_button(self, text: str, command: Optional[Callable] = None, 
                   style: str = "default") -> ttk.Button:
        """
        Add a button to the dialog.
        
        Args:
            text: Button text
            command: Button command callback
            style: Button style ('default', 'primary', 'danger')
        
        Returns:
            Created button widget
        """
        if style == "primary":
            btn = ttk.Button(
                self.buttons_frame,
                text=text,
                command=command or self._on_ok
            )
        elif style == "danger":
            btn = ttk.Button(
                self.buttons_frame,
                text=text,
                command=command or self._on_cancel
            )
        else:
            btn = ttk.Button(
                self.buttons_frame,
                text=text,
                command=command or self._on_cancel
            )
        
        btn.pack(side=tk.RIGHT, padx=(5, 0))
        return btn
    
    def _on_ok(self):
        """Handle OK button click."""
        self.result = True
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """
        Show the modal and wait for user interaction.
        
        Returns:
            True if OK/confirmed, False if cancelled
        """
        self.parent.wait_window(self.dialog)
        return self.result if self.result is not None else False


class DatePicker:
    """
    Date picker component using calendar widget.
    """
    
    def __init__(self, parent: ttk.Frame, label_text: str = "Date:", 
                 required: bool = False, initial_value: Optional[str] = None):
        """
        Initialize date picker.
        
        Args:
            parent: Parent frame
            label_text: Label text
            required: Whether field is required
            initial_value: Initial date value (YYYY-MM-DD format)
        """
        self.frame = ttk.Frame(parent)
        self.required = required
        self.value = tk.StringVar(value=initial_value or "")
        
        # Label
        label_frame = ttk.Frame(self.frame)
        label_frame.pack(side=tk.LEFT)
        label = ttk.Label(label_frame, text=label_text)
        label.pack(side=tk.LEFT)
        if required:
            required_label = ttk.Label(label_frame, text="*", foreground="red")
            required_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # Entry field
        self.entry = ttk.Entry(self.frame, textvariable=self.value, width=12)
        self.entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Calendar button
        self.cal_btn = ttk.Button(
            self.frame,
            text="📅",
            command=self._show_calendar,
            width=3
        )
        self.cal_btn.pack(side=tk.LEFT)
        
        # Set placeholder text if no initial value provided
        if not initial_value:
            self.entry.insert(0, "YYYY-MM-DD")
            self.entry.config(foreground="gray")
            self.entry.bind("<FocusIn>", self._on_focus_in)
            self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Handle focus in event."""
        if self.entry.get() == "YYYY-MM-DD":
            self.entry.delete(0, tk.END)
            self.entry.config(foreground="black")
    
    def _on_focus_out(self, event):
        """Handle focus out event."""
        if not self.entry.get():
            self.entry.insert(0, "YYYY-MM-DD")
            self.entry.config(foreground="gray")
    
    def _show_calendar(self):
        """Show calendar picker dialog."""
        cal_dialog = tk.Toplevel(self.frame.winfo_toplevel())
        cal_dialog.title("Select Date")
        cal_dialog.geometry("300x300")
        cal_dialog.transient(self.frame.winfo_toplevel())
        cal_dialog.grab_set()
        
        # Get current date or selected date
        current_value = self.value.get()
        if current_value and current_value != "YYYY-MM-DD":
            try:
                current_date = datetime.strptime(current_value, "%Y-%m-%d").date()
            except ValueError:
                current_date = date.today()
        else:
            current_date = date.today()
        
        # Calendar widget
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        cal_frame = ttk.Frame(cal_dialog, padding="10")
        cal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Month/Year navigation
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.pack(pady=(0, 10))
        
        year = current_date.year
        month = current_date.month
        
        def update_calendar():
            """Update calendar display."""
            for widget in days_frame.winfo_children():
                widget.destroy()
            
            # Month/Year label
            month_label.config(text=f"{calendar.month_name[month]} {year}")
            
            # Day buttons
            month_days = cal.monthdayscalendar(year, month)
            for week in month_days:
                week_frame = ttk.Frame(days_frame)
                week_frame.pack()
                for day in week:
                    if day == 0:
                        ttk.Label(week_frame, text="", width=4).pack(side=tk.LEFT)
                    else:
                        day_btn = ttk.Button(
                            week_frame,
                            text=str(day),
                            width=4,
                            command=lambda d=day: select_date(d)
                        )
                        if day == current_date.day and month == current_date.month and year == current_date.year:
                            day_btn.config(style="TButton")
                        day_btn.pack(side=tk.LEFT, padx=1, pady=1)
        
        def select_date(day: int):
            """Select a date."""
            selected_date = date(year, month, day)
            self.value.set(selected_date.strftime("%Y-%m-%d"))
            self.entry.config(foreground="black")
            cal_dialog.destroy()
        
        def prev_month():
            """Go to previous month."""
            nonlocal month, year
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            update_calendar()
        
        def next_month():
            """Go to next month."""
            nonlocal month, year
            month += 1
            if month > 12:
                month = 1
                year += 1
            update_calendar()
        
        # Navigation buttons
        ttk.Button(nav_frame, text="◀", command=prev_month, width=3).pack(side=tk.LEFT)
        month_label = ttk.Label(nav_frame, text="", font=("Segoe UI", 10, "bold"))
        month_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="▶", command=next_month, width=3).pack(side=tk.LEFT)
        
        # Days frame
        days_frame = ttk.Frame(cal_frame)
        days_frame.pack()
        
        # Day headers
        headers = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        header_frame = ttk.Frame(cal_frame)
        header_frame.pack()
        for header in headers:
            ttk.Label(header_frame, text=header, font=("Segoe UI", 9, "bold"), width=4).pack(side=tk.LEFT)
        
        update_calendar()
    
    def get(self) -> Optional[str]:
        """Get the selected date value."""
        value = self.value.get()
        if value and value != "YYYY-MM-DD":
            return value
        return None
    
    def pack(self, **kwargs):
        """Pack the date picker frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the date picker frame."""
        self.frame.grid(**kwargs)


class StatusBadge:
    """Status badge component with color coding."""
    
    STATUS_COLORS = {
        "Pending": ("#F59E0B", "#FEF3C7"),  # Amber
        "Verified": ("#3B82F6", "#DBEAFE"),  # Blue
        "Settled": ("#10B981", "#D1FAE5"),  # Green
        "Rejected": ("#EF4444", "#FEE2E2"),  # Red
        "Active": ("#10B981", "#D1FAE5"),
        "Inactive": ("#6B7280", "#F3F4F6"),
    }
    
    @staticmethod
    def create(parent: ttk.Frame, status: str, row: int = 0, column: int = 0) -> ttk.Label:
        """
        Create a status badge.
        
        Args:
            parent: Parent frame
            status: Status text
            row: Grid row
            column: Grid column
        
        Returns:
            Label widget styled as badge
        """
        fg_color, bg_color = StatusBadge.STATUS_COLORS.get(
            status, 
            ("#6B7280", "#F3F4F6")  # Default gray
        )
        
        badge = ttk.Label(
            parent,
            text=status,
            font=("Segoe UI", 9, "bold"),
            foreground=fg_color,
            background=bg_color,
            padding=(6, 3),
            relief="solid",
            borderwidth=1
        )
        badge.grid(row=row, column=column, padx=2, pady=2, sticky=tk.W)
        return badge


class LoadingIndicator:
    """Loading indicator component."""
    
    @staticmethod
    def show(parent: tk.Widget, message: str = "Loading..."):
        """
        Show loading indicator.
        
        Args:
            parent: Parent widget
            message: Loading message
        
        Returns:
            Toplevel window with loading indicator
        """
        loading = tk.Toplevel(parent)
        loading.title("Loading")
        loading.geometry("300x100")
        loading.resizable(False, False)
        loading.transient(parent)
        loading.grab_set()
        
        # Center
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 50
        loading.geometry(f"+{x}+{y}")
        
        loading.configure(bg=WHITE)
        
        frame = ttk.Frame(loading, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=message, font=("Segoe UI", 10)).pack()
        
        # Progress bar
        progress = ttk.Progressbar(frame, mode='indeterminate')
        progress.pack(pady=(10, 0), fill=tk.X)
        progress.start()
        
        return loading


class EmptyState:
    """Empty state message component."""
    
    @staticmethod
    def show(parent: ttk.Frame, message: str, action_text: Optional[str] = None,
             action_command: Optional[Callable] = None):
        """
        Show empty state message.
        
        Args:
            parent: Parent frame
            message: Message text
            action_text: Optional action button text
            action_command: Optional action button command
        """
        empty_frame = ttk.Frame(parent)
        empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
        
        # Icon/emoji
        icon_label = ttk.Label(
            empty_frame,
            text="📋",
            font=("Segoe UI", 48)
        )
        icon_label.pack(pady=(0, 20))
        
        # Message
        msg_label = ttk.Label(
            empty_frame,
            text=message,
            font=("Segoe UI", 12),
            foreground=GRAY_TEXT
        )
        msg_label.pack(pady=(0, 10))
        
        # Action button
        if action_text and action_command:
            ttk.Button(
                empty_frame,
                text=action_text,
                command=action_command
            ).pack()


def create_tooltip(widget: tk.Widget, text: str):
    """
    Create a tooltip for a widget.
    
    Args:
        widget: Widget to attach tooltip to
        text: Tooltip text
    """
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = ttk.Label(
            tooltip,
            text=text,
            background="#FFFFCC",
            foreground="black",
            relief="solid",
            borderwidth=1,
            padding=5,
            font=("Segoe UI", 9)
        )
        label.pack()
        
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

