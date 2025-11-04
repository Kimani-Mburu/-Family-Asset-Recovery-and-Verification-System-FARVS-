"""
Tkinter/ttk theming helpers for FARVS.

Provides a light/dark theme switch and base widget styling to improve
readability and aesthetics without external dependencies.
"""

import tkinter as tk
from tkinter import ttk


def apply_base_styles(style: ttk.Style) -> None:
    """Apply base styles for common widgets."""
    # General paddings and fonts
    style.configure("TLabel", padding=(2, 2))
    style.configure("TButton", padding=(8, 6))
    style.configure("TEntry", padding=(4, 3))
    style.configure("TCombobox", padding=(4, 3))
    style.configure("TLabelframe", padding=(10, 8))
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    # Treeview header styling
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        padding=(6, 4),
    )

    # Treeview row height
    style.configure("Treeview", rowheight=24)


def set_theme(root: tk.Tk, theme: str) -> None:
    """Set light/dark theme. Theme options: 'light', 'dark', 'system'."""
    style = ttk.Style(root)
    # Choose a base theme available across platforms
    # 'clam' tends to be consistent; for dark we tweak colors manually
    base = "clam"
    try:
        style.theme_use(base)
    except Exception:
        pass

    apply_base_styles(style)

    if theme == "dark":
        # Palette for dark mode
        bg = "#1f2430"
        fg = "#e6e6e6"
        acc = "#3d7eff"
        sel = "#2b3245"

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg)
        style.configure("TButton", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground="#2a2f3c", foreground=fg)
        style.configure("TCombobox", fieldbackground="#2a2f3c", foreground=fg)

        style.configure(
            "Treeview",
            background="#222735",
            fieldbackground="#222735",
            foreground=fg,
        )
        style.map("Treeview", background=[("selected", sel)])
        style.configure("Treeview.Heading", background=bg, foreground=fg)
    else:
        # Light/system defaults with small tweaks
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#111111")
        style.map("Treeview", background=[("selected", "#e6f0ff")])


def stripe_treeview(tree: ttk.Treeview) -> None:
    """Apply zebra striping to a Treeview (call after population)."""
    # Assign tags to each item
    for idx, item in enumerate(tree.get_children("")):
        tag = "oddrow" if idx % 2 else "evenrow"
        tree.item(item, tags=(tag,))

    # Configure tag colors (works with both light/dark)
    tree.tag_configure("evenrow", background="#f7f9fc")
    tree.tag_configure("oddrow", background="#eef3fa")



