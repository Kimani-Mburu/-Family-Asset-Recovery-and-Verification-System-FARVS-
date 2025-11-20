"""
Scrolling Utilities for FARVS
==============================

Provides enhanced scrolling functionality for treeviews and canvas-based widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


def bind_mousewheel(widget, command=None):
    """
    Bind mousewheel scrolling to a widget.
    
    Args:
        widget: The widget to bind mousewheel events to
        command: Optional command to execute on scroll (defaults to widget.yview_scroll)
    """
    def on_mousewheel(event):
        """Handle mousewheel events."""
        if command:
            command(event)
        else:
            if hasattr(widget, 'yview_scroll'):
                widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif hasattr(widget, 'canvas') and hasattr(widget.canvas, 'yview_scroll'):
                widget.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Bind to widget and all children
    widget.bind("<MouseWheel>", on_mousewheel)
    widget.bind("<Button-4>", lambda e: on_mousewheel(type('obj', (object,), {'delta': 120})()))
    widget.bind("<Button-5>", lambda e: on_mousewheel(type('obj', (object,), {'delta': -120})()))
    
    # Also bind to parent for better coverage
    parent = widget.winfo_parent()
    if parent:
        try:
            parent_widget = widget._nametowidget(parent)
            parent_widget.bind("<MouseWheel>", lambda e: on_mousewheel(e) if widget.winfo_containing(e.x_root, e.y_root) == widget else None)
        except:
            pass


def update_scrollregion(widget):
    """
    Update the scrollregion of a canvas widget.
    
    Args:
        widget: Canvas widget or widget containing a canvas
    """
    if hasattr(widget, 'canvas'):
        canvas = widget.canvas
    elif isinstance(widget, tk.Canvas):
        canvas = widget
    else:
        return
    
    try:
        canvas.update_idletasks()
        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=bbox)
    except:
        pass


def configure_treeview_scrolling(treeview: ttk.Treeview, parent_frame: ttk.Frame):
    """
    Configure proper scrolling for a treeview with enhanced mousewheel support.
    Uses a comprehensive approach that ensures proper container configuration.
    
    Args:
        treeview: The treeview widget
        parent_frame: The parent frame containing the treeview
    """
    # CRITICAL: Ensure parent frame is properly configured for scrolling
    # Note: Since treeview now uses pack(), we don't need grid_configure
    # The parent frame should already be configured with grid weights by the caller
    
    # Get root window
    root = treeview.winfo_toplevel()
    
    # Simple mousewheel handler
    def on_mousewheel(event):
        """Handle mousewheel events."""
        try:
            # Always scroll if event is on treeview or parent
            if hasattr(event, 'delta'):
                delta = int(-1 * (event.delta / 120))
            else:
                delta = -1 if event.num == 4 else 1
            treeview.yview_scroll(delta, "units")
            return "break"
        except:
            pass
    
    # Bind to treeview directly
    treeview.bind("<MouseWheel>", on_mousewheel)
    treeview.bind("<Button-4>", lambda e: treeview.yview_scroll(-1, "units"))
    treeview.bind("<Button-5>", lambda e: treeview.yview_scroll(1, "units"))
    
    # Bind to parent frame
    parent_frame.bind("<MouseWheel>", on_mousewheel)
    parent_frame.bind("<Button-4>", lambda e: treeview.yview_scroll(-1, "units"))
    parent_frame.bind("<Button-5>", lambda e: treeview.yview_scroll(1, "units"))
    
    # Bind to root window for global scrolling
    def on_root_mousewheel(event):
        """Handle mousewheel on root window."""
        try:
            focused = root.focus_get()
            # Check if focus is on treeview or any child
            if focused == treeview:
                if hasattr(event, 'delta'):
                    delta = int(-1 * (event.delta / 120))
                else:
                    delta = -1 if event.num == 4 else 1
                treeview.yview_scroll(delta, "units")
                return "break"
        except:
            pass
    
    # Use bind_all with add="+" to not override other bindings
    root.bind_all("<MouseWheel>", on_root_mousewheel, add="+")
    root.bind_all("<Button-4>", lambda e: treeview.yview_scroll(-1, "units") if root.focus_get() == treeview else None, add="+")
    root.bind_all("<Button-5>", lambda e: treeview.yview_scroll(1, "units") if root.focus_get() == treeview else None, add="+")

