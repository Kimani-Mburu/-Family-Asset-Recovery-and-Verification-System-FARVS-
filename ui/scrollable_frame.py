"""
Scrollable Frame Widget for FARVS
===================================

A robust scrollable frame implementation using Canvas + Frame approach.
This solves the persistent scrolling issues by using the recommended
Canvas-based scrolling pattern.

Usage:
    from ui.scrollable_frame import ScrollableFrame
    
    scrollable = ScrollableFrame(parent)
    scrollable.pack(fill=tk.BOTH, expand=True)
    
    # Add widgets to scrollable.inner_frame
    label = ttk.Label(scrollable.inner_frame, text="Content")
    label.pack()
"""

import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame widget that uses Canvas + Frame approach.
    
    This is the recommended solution for scrolling in Tkinter when
    content exceeds the visible area.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize scrollable frame.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments passed to ttk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.inner_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create window in canvas for inner frame
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw"
        )
        
        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mousewheel binding
        self._bind_mousewheel()
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _on_frame_configure(self, event):
        """Update scroll region when inner frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize inner frame to match canvas width."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """Bind mousewheel events for scrolling."""
        def on_mousewheel(event):
            """Handle mousewheel scrolling."""
            # Windows/Mac
            if hasattr(event, 'delta'):
                delta = int(-1 * (event.delta / 120))
            else:
                # Linux
                delta = -1 if event.num == 4 else 1
            self.canvas.yview_scroll(delta, "units")
            return "break"
        
        # Bind to canvas and inner frame
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Also bind to inner frame
        self.inner_frame.bind("<MouseWheel>", on_mousewheel)
        self.inner_frame.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.inner_frame.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Bind to root for global scrolling
        root = self.winfo_toplevel()
        def on_root_mousewheel(event):
            """Handle mousewheel on root when frame has focus."""
            try:
                focused = root.focus_get()
                if focused == self.canvas or focused == self.inner_frame:
                    if hasattr(event, 'delta'):
                        delta = int(-1 * (event.delta / 120))
                    else:
                        delta = -1 if event.num == 4 else 1
                    self.canvas.yview_scroll(delta, "units")
                    return "break"
            except:
                pass
        
        root.bind_all("<MouseWheel>", on_root_mousewheel, add="+")
        root.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units") if root.focus_get() in (self.canvas, self.inner_frame) else None, add="+")
        root.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units") if root.focus_get() in (self.canvas, self.inner_frame) else None, add="+")

