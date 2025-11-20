"""
Tkinter/ttk theming helpers for FARVS.

Provides blue and white theme styling to improve readability and aesthetics.
All UI components use a consistent blue and white color scheme.
"""

import tkinter as tk
from tkinter import ttk


# Blue and White Color Palette
BLUE_PRIMARY = "#1E3A8A"      # Primary blue for headers and important elements
BLUE_SECONDARY = "#3B82F6"    # Secondary blue for buttons and highlights
BLUE_LIGHT = "#DBEAFE"        # Light blue for backgrounds and hover states
BLUE_ACCENT = "#2563EB"       # Accent blue for active states
WHITE = "#FFFFFF"              # Pure white for backgrounds
WHITE_OFF = "#F8FAFC"          # Off-white for alternate rows
GRAY_TEXT = "#1F2937"          # Dark gray for text
GRAY_LIGHT = "#E5E7EB"         # Light gray for borders


def apply_base_styles(style: ttk.Style) -> None:
    """
    Apply base styles for common widgets with blue and white theme.
    
    Args:
        style: The ttk.Style object to configure
    """
    # General paddings and fonts
    style.configure("TLabel", padding=(2, 2), font=("Segoe UI", 9))
    style.configure("TButton", padding=(8, 6), font=("Segoe UI", 9, "bold"))
    style.configure("TEntry", padding=(4, 3), font=("Segoe UI", 9))
    style.configure("TCombobox", padding=(4, 3), font=("Segoe UI", 9))
    style.configure("TLabelframe", padding=(10, 8), background=WHITE)
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), 
                    background=WHITE, foreground=BLUE_PRIMARY)

    # Treeview header styling with blue theme
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        padding=(6, 4),
        background=BLUE_PRIMARY,
        foreground=WHITE,
    )

    # Treeview row height
    style.configure("Treeview", rowheight=24)


def set_theme(root: tk.Tk, theme: str = "light") -> None:
    """
    Set blue and white theme for the application.
    
    Args:
        root: The root Tkinter window
        theme: Theme name (currently only 'light' with blue/white is supported)
    """
    style = ttk.Style(root)
    # Use 'clam' theme as base for better cross-platform compatibility
    base = "clam"
    try:
        style.theme_use(base)
    except Exception:
        pass

    apply_base_styles(style)

    # Blue and White Theme Configuration
    # Main background - white
    root.configure(bg=WHITE)
    style.configure("TFrame", background=WHITE)
    style.configure("TLabel", background=WHITE, foreground=GRAY_TEXT)
    style.configure("TLabelframe", background=WHITE, borderwidth=1, 
                    relief="solid", bordercolor=GRAY_LIGHT)
    style.configure("TLabelframe.Label", background=WHITE, 
                    foreground=BLUE_PRIMARY)

    # Buttons - blue theme
    style.configure("TButton", 
                    background=BLUE_SECONDARY, 
                    foreground=WHITE,
                    borderwidth=0,
                    focuscolor="none")
    style.map("TButton",
              background=[("active", BLUE_ACCENT),
                         ("pressed", BLUE_PRIMARY)],
              foreground=[("active", WHITE),
                         ("pressed", WHITE)])

    # Entry fields - white background with blue border on focus
    style.configure("TEntry", 
                    fieldbackground=WHITE, 
                    foreground=GRAY_TEXT,
                    borderwidth=1,
                    relief="solid",
                    bordercolor=GRAY_LIGHT)
    style.map("TEntry",
              fieldbackground=[("focus", WHITE)],
              bordercolor=[("focus", BLUE_SECONDARY)])

    # Combobox - white background
    style.configure("TCombobox", 
                    fieldbackground=WHITE, 
                    foreground=GRAY_TEXT,
                    borderwidth=1,
                    relief="solid",
                    bordercolor=GRAY_LIGHT)
    style.map("TCombobox",
              fieldbackground=[("readonly", WHITE)],
              bordercolor=[("focus", BLUE_SECONDARY)])

    # Treeview - white background with blue selection
    style.configure("Treeview",
                    background=WHITE,
                    fieldbackground=WHITE,
                    foreground=GRAY_TEXT,
                    borderwidth=1,
                    relief="solid")
    style.map("Treeview", 
              background=[("selected", BLUE_SECONDARY)],
              foreground=[("selected", WHITE)])
    style.configure("Treeview.Heading", 
                    background=BLUE_PRIMARY, 
                    foreground=WHITE,
                    borderwidth=1,
                    relief="solid")

    # Notebook (tabs) - blue theme
    style.configure("TNotebook", background=WHITE, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=BLUE_LIGHT,
                    foreground=BLUE_PRIMARY,
                    padding=(12, 6),
                    font=("Segoe UI", 9, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", BLUE_SECONDARY),
                         ("active", BLUE_ACCENT)],
              foreground=[("selected", WHITE),
                         ("active", WHITE)])


def stripe_treeview(tree: ttk.Treeview) -> None:
    """
    Apply zebra striping to a Treeview with blue and white theme.
    
    Args:
        tree: The Treeview widget to apply striping to
    """
    # Assign tags to each item for alternating row colors
    for idx, item in enumerate(tree.get_children("")):
        tag = "oddrow" if idx % 2 else "evenrow"
        tree.item(item, tags=(tag,))

    # Configure tag colors with blue and white theme
    tree.tag_configure("evenrow", background=WHITE)
    tree.tag_configure("oddrow", background=WHITE_OFF)



