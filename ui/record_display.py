"""
Enhanced Record Display Components for FARVS

This module provides modern, visually appealing ways to display records
with cards, detailed views, and better formatting.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from ui.theme import BLUE_PRIMARY, BLUE_SECONDARY, BLUE_LIGHT, WHITE, GRAY_TEXT, GRAY_LIGHT
from ui.components import StatusBadge


class RecordCard:
    """Modern card-based record display component."""
    
    def __init__(self, parent: tk.Widget, record: Dict[str, Any], 
                 on_select: Optional[Callable] = None, card_type: str = "default"):
        """
        Create a record card.
        
        Args:
            parent: Parent widget
            record: Record data dictionary
            on_select: Callback when card is clicked
            card_type: Type of card ('deceased', 'asset', 'claim', 'claimant')
        """
        self.record = record
        self.on_select = on_select
        self.card_type = card_type
        
        # Create card frame
        self.card = tk.Frame(
            parent,
            bg=WHITE,
            relief="solid",
            borderwidth=1,
            bd=1,
            cursor="hand2" if on_select else "arrow"
        )
        
        if on_select:
            self.card.bind("<Button-1>", lambda e: on_select(record))
            self.card.bind("<Enter>", self._on_enter)
            self.card.bind("<Leave>", self._on_leave)
        
        self._create_card_content()
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.card.config(bg=BLUE_LIGHT, relief="solid", borderwidth=2)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.card.config(bg=WHITE, relief="solid", borderwidth=1)
    
    def _create_card_content(self):
        """Create card content based on type."""
        if self.card_type == "deceased":
            self._create_deceased_card()
        elif self.card_type == "asset":
            self._create_asset_card()
        elif self.card_type == "claim":
            self._create_claim_card()
        elif self.card_type == "claimant":
            self._create_claimant_card()
        else:
            self._create_default_card()
    
    def _create_deceased_card(self):
        """Create deceased record card."""
        content = tk.Frame(self.card, bg=WHITE, padx=15, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header with icon and name
        header = tk.Frame(content, bg=WHITE)
        header.pack(fill=tk.X, pady=(0, 8))
        
        icon_label = tk.Label(header, text="👤", font=("Segoe UI", 20), bg=WHITE)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        name_frame = tk.Frame(header, bg=WHITE)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        name = f"{self.record.get('FirstName', '')} {self.record.get('LastName', '')}"
        name_label = tk.Label(
            name_frame,
            text=name,
            font=("Segoe UI", 12, "bold"),
            bg=WHITE,
            fg=BLUE_PRIMARY,
            anchor=tk.W
        )
        name_label.pack(anchor=tk.W)
        
        # Details
        details_frame = tk.Frame(content, bg=WHITE)
        details_frame.pack(fill=tk.X)
        
        if self.record.get('NationalId'):
            tk.Label(
                details_frame,
                text=f"ID: {self.record['NationalId']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('DateOfBirth'):
            dob = str(self.record['DateOfBirth'])[:10] if len(str(self.record['DateOfBirth'])) > 10 else str(self.record['DateOfBirth'])
            tk.Label(
                details_frame,
                text=f"Born: {dob}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('DateOfDeath'):
            dod = str(self.record['DateOfDeath'])[:10] if len(str(self.record['DateOfDeath'])) > 10 else str(self.record['DateOfDeath'])
            tk.Label(
                details_frame,
                text=f"Died: {dod}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
    
    def _create_asset_card(self):
        """Create asset record card."""
        content = tk.Frame(self.card, bg=WHITE, padx=15, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(content, bg=WHITE)
        header.pack(fill=tk.X, pady=(0, 8))
        
        asset_type = self.record.get('AssetType', 'Asset')
        icon = "💰" if "Bank" in asset_type else "📋" if "Policy" in asset_type else "💼"
        
        icon_label = tk.Label(header, text=icon, font=("Segoe UI", 20), bg=WHITE)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        type_frame = tk.Frame(header, bg=WHITE)
        type_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            type_frame,
            text=asset_type,
            font=("Segoe UI", 12, "bold"),
            bg=WHITE,
            fg=BLUE_PRIMARY,
            anchor=tk.W
        ).pack(anchor=tk.W)
        
        # Value
        value = self.record.get('EstimatedValue', 0)
        if value:
            value_str = f"${value:,.2f}"
            tk.Label(
                type_frame,
                text=value_str,
                font=("Segoe UI", 11, "bold"),
                bg=WHITE,
                fg="#10B981",
                anchor=tk.W
            ).pack(anchor=tk.W, pady=(2, 0))
        
        # Details
        details_frame = tk.Frame(content, bg=WHITE)
        details_frame.pack(fill=tk.X)
        
        if self.record.get('DeceasedName'):
            tk.Label(
                details_frame,
                text=f"Deceased: {self.record['DeceasedName']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('InstitutionName'):
            tk.Label(
                details_frame,
                text=f"Institution: {self.record['InstitutionName']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('Identifier'):
            tk.Label(
                details_frame,
                text=f"ID: {self.record['Identifier']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
    
    def _create_claim_card(self):
        """Create claim record card."""
        content = tk.Frame(self.card, bg=WHITE, padx=15, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header with status
        header = tk.Frame(content, bg=WHITE)
        header.pack(fill=tk.X, pady=(0, 8))
        
        claim_id = self.record.get('ClaimId', 'N/A')
        tk.Label(
            header,
            text=f"Claim #{claim_id}",
            font=("Segoe UI", 11, "bold"),
            bg=WHITE,
            fg=BLUE_PRIMARY
        ).pack(side=tk.LEFT)
        
        # Status badge
        status = self.record.get('Status', 'Pending')
        status_frame = tk.Frame(header, bg=WHITE)
        status_frame.pack(side=tk.RIGHT)
        StatusBadge.create(status_frame, status, row=0, column=0)
        
        # Details
        details_frame = tk.Frame(content, bg=WHITE)
        details_frame.pack(fill=tk.X)
        
        if self.record.get('AssetName'):
            tk.Label(
                details_frame,
                text=f"Asset: {self.record['AssetName']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('ClaimantName'):
            tk.Label(
                details_frame,
                text=f"Claimant: {self.record['ClaimantName']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('FiledAt'):
            filed = str(self.record['FiledAt'])[:10] if len(str(self.record['FiledAt'])) > 10 else str(self.record['FiledAt'])
            tk.Label(
                details_frame,
                text=f"Filed: {filed}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
    
    def _create_claimant_card(self):
        """Create claimant record card."""
        content = tk.Frame(self.card, bg=WHITE, padx=15, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(content, bg=WHITE)
        header.pack(fill=tk.X, pady=(0, 8))
        
        icon_label = tk.Label(header, text="👥", font=("Segoe UI", 20), bg=WHITE)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        name_frame = tk.Frame(header, bg=WHITE)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        name = f"{self.record.get('FirstName', '')} {self.record.get('LastName', '')}"
        tk.Label(
            name_frame,
            text=name,
            font=("Segoe UI", 12, "bold"),
            bg=WHITE,
            fg=BLUE_PRIMARY,
            anchor=tk.W
        ).pack(anchor=tk.W)
        
        # Details
        details_frame = tk.Frame(content, bg=WHITE)
        details_frame.pack(fill=tk.X)
        
        if self.record.get('Relationship'):
            tk.Label(
                details_frame,
                text=f"Relationship: {self.record['Relationship']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
        
        if self.record.get('Contact'):
            tk.Label(
                details_frame,
                text=f"Contact: {self.record['Contact']}",
                font=("Segoe UI", 9),
                bg=WHITE,
                fg=GRAY_TEXT
            ).pack(anchor=tk.W, pady=2)
    
    def _create_default_card(self):
        """Create default card for unknown types."""
        content = tk.Frame(self.card, bg=WHITE, padx=15, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text=str(self.record),
            font=("Segoe UI", 10),
            bg=WHITE,
            anchor=tk.W
        ).pack(anchor=tk.W)
    
    def pack(self, **kwargs):
        """Pack the card."""
        self.card.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the card."""
        self.card.grid(**kwargs)


class RecordGridView:
    """Grid view for displaying records as cards."""
    
    def __init__(self, parent: ttk.Frame, card_type: str = "default", 
                 columns: int = 3, on_select: Optional[Callable] = None):
        """
        Initialize grid view.
        
        Args:
            parent: Parent frame
            card_type: Type of cards to display
            columns: Number of columns in grid
            on_select: Callback when card is selected
        """
        self.parent = parent
        self.card_type = card_type
        self.columns = columns
        self.on_select = on_select
        self.cards: List[RecordCard] = []
        
        # Create scrollable frame
        self.canvas = tk.Canvas(parent, bg=WHITE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#F8FAFC")
        
        def update_scroll_region(event=None):
            """Update scroll region when content changes."""
            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
        
        self.scrollable_frame.bind("<Configure>", update_scroll_region)
        
        # Create canvas window with proper configuration
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to resize window with content
        def configure_canvas_window(event=None):
            """Resize canvas window to fit content."""
            canvas_width = event.width if event else self.canvas.winfo_width()
            if canvas_width > 1:
                self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind("<Configure>", configure_canvas_window)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mousewheel for scrolling - simpler approach
        def on_mousewheel(event):
            """Handle mousewheel scrolling."""
            try:
                # Get root window
                root = self.canvas.winfo_toplevel()
                x, y = root.winfo_pointerxy()
                
                # Check if mouse is over canvas or scrollable frame
                canvas_x = self.canvas.winfo_rootx()
                canvas_y = self.canvas.winfo_rooty()
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if (canvas_x <= x <= canvas_x + canvas_width and 
                    canvas_y <= y <= canvas_y + canvas_height):
                    if hasattr(event, 'delta'):
                        delta = int(-1 * (event.delta / 120))
                    else:
                        delta = -1 if event.num == 4 else 1
                    self.canvas.yview_scroll(delta, "units")
                    return "break"
            except:
                pass
        
        # Bind to canvas and scrollable frame
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        self.scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.scrollable_frame.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        
        # Also bind to root for global scrolling
        root = self.canvas.winfo_toplevel()
        def on_root_mousewheel(event):
            focused = root.focus_get()
            if focused == self.canvas or str(focused).startswith(str(self.canvas)):
                if hasattr(event, 'delta'):
                    delta = int(-1 * (event.delta / 120))
                else:
                    delta = -1 if event.num == 4 else 1
                self.canvas.yview_scroll(delta, "units")
                return "break"
        
        root.bind_all("<MouseWheel>", on_root_mousewheel)
        
        # Configure grid
        for i in range(columns):
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="cols")
    
    def display_records(self, records: List[Dict[str, Any]]):
        """Display records as cards in grid."""
        # Clear existing cards
        for card in self.cards:
            card.card.destroy()
        self.cards.clear()
        
        if not records:
            # Update scroll region even when empty
            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
            return
        
        # Create cards
        for i, record in enumerate(records):
            row = i // self.columns
            col = i % self.columns
            
            card = RecordCard(
                self.scrollable_frame,
                record,
                on_select=self.on_select,
                card_type=self.card_type
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.cards.append(card)
        
        # Update scroll region after adding cards
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)
    
    def pack(self, **kwargs):
        """Pack the grid view."""
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def grid(self, **kwargs):
        """Grid the grid view."""
        # Extract row, column, and sticky from kwargs to avoid duplicates
        row = kwargs.get('row', 0)
        column = kwargs.get('column', 0)
        sticky = kwargs.get('sticky', (tk.W, tk.E, tk.N, tk.S))
        
        # Remove row, column, sticky from kwargs before passing to grid
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['row', 'column', 'sticky']}
        
        self.canvas.grid(row=row, column=column, sticky=sticky, **filtered_kwargs)
        self.scrollbar.grid(row=row, column=column + 1 if 'column' in kwargs else 1,
                           sticky=(tk.N, tk.S))


class EnhancedTreeview:
    """Enhanced treeview with better formatting and features."""
    
    def __init__(self, parent: ttk.Frame, columns: List[str], 
                 column_widths: Optional[Dict[str, int]] = None,
                 height: int = 15):
        """
        Create enhanced treeview.
        
        Args:
            parent: Parent frame
            columns: List of column names
            column_widths: Dictionary of column widths
            height: Treeview height
        """
        self.parent = parent
        self.columns = columns
        
        # Create frame
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=height)
        
        # Configure columns
        default_widths = {col: 100 for col in columns}
        if column_widths:
            default_widths.update(column_widths)
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=default_widths.get(col, 100), anchor=tk.W)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def insert_record(self, record: Dict[str, Any], values_formatter: Optional[Callable] = None):
        """
        Insert a record with formatted values.
        
        Args:
            record: Record dictionary
            values_formatter: Optional function to format values
        """
        if values_formatter:
            values = values_formatter(record)
        else:
            values = tuple(record.get(col, '') for col in self.columns)
        
        item = self.tree.insert("", tk.END, values=values)
        return item
    
    def clear(self):
        """Clear all items."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def bind_select(self, callback: Callable):
        """Bind selection event."""
        self.tree.bind("<<TreeviewSelect>>", callback)

