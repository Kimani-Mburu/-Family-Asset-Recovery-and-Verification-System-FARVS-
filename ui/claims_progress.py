"""
Complete Claims Progress Tracker for FARVS

This module provides a comprehensive progress tracking visualization
for claims with timeline, dates, and detailed status information.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from datetime import datetime, date

from ui.theme import BLUE_PRIMARY, BLUE_SECONDARY, BLUE_LIGHT, WHITE, GRAY_TEXT, GRAY_LIGHT
from ui.components import StatusBadge
from logging_config import get_logger

logger = get_logger(__name__)


class ClaimsProgressTracker:
    """
    Complete claims progress tracker with timeline and detailed information.
    
    Shows the full journey of a claim from Pending → Verified → Settled
    with dates, timestamps, and visual progress indicators.
    """
    
    # Status definitions with colors and icons
    STATUSES = {
        "Pending": {
            "icon": "⏳",
            "color": "#F59E0B",
            "bg_color": "#FEF3C7",
            "description": "Claim submitted, awaiting verification"
        },
        "Verified": {
            "icon": "✅",
            "color": "#3B82F6",
            "bg_color": "#DBEAFE",
            "description": "Claim verified, ready for settlement"
        },
        "Settled": {
            "icon": "✔️",
            "color": "#10B981",
            "bg_color": "#D1FAE5",
            "description": "Claim settled and payment processed"
        },
        "Rejected": {
            "icon": "❌",
            "color": "#EF4444",
            "bg_color": "#FEE2E2",
            "description": "Claim rejected"
        }
    }
    
    def __init__(self, parent: ttk.Frame, claim_data: Optional[Dict[str, Any]] = None):
        """
        Initialize progress tracker.
        
        Args:
            parent: Parent frame
            claim_data: Optional claim data dictionary
        """
        self.parent = parent
        self.claim_data = claim_data or {}
        self.progress_frame = None
        self.timeline_frame = None
        
        self._create_progress_tracker()
        if claim_data:
            self.update_progress(claim_data)
    
    def _create_progress_tracker(self):
        """Create the progress tracker UI."""
        # Main container
        self.progress_frame = ttk.Frame(self.parent)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        # Progress steps container
        self.steps_container = tk.Frame(self.progress_frame, bg="#F8FAFC", relief="solid", borderwidth=1)
        self.steps_container.pack(fill=tk.X, padx=10, pady=10)
        
        # Steps frame
        self.steps_frame = tk.Frame(self.steps_container, bg="#F8FAFC")
        self.steps_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Create step indicators
        self.steps = []
        step_names = ["Pending", "Verified", "Settled"]
        
        for i, step_name in enumerate(step_names):
            step = self._create_step_indicator(step_name, i, len(step_names))
            self.steps.append(step)
        
        # Timeline section (for detailed dates)
        self.timeline_frame = ttk.LabelFrame(self.progress_frame, text="Timeline", padding="15")
        self.timeline_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Timeline content (will be populated when claim data is available)
        self.timeline_content = ttk.Frame(self.timeline_frame)
        self.timeline_content.pack(fill=tk.X)
    
    def _create_step_indicator(self, step_name: str, index: int, total_steps: int):
        """Create a single step indicator."""
        step_info = self.STATUSES.get(step_name, {})
        
        # Step container
        step_container = tk.Frame(self.steps_frame, bg="#F8FAFC")
        step_container.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Step circle (larger, more prominent)
        circle_frame = tk.Frame(step_container, bg="#F8FAFC")
        circle_frame.pack(pady=(0, 10))
        
        circle = tk.Canvas(
            circle_frame,
            width=60,
            height=60,
            highlightthickness=0,
            bg="#F8FAFC"
        )
        circle.pack()
        
        # Default state (inactive)
        circle.create_oval(10, 10, 50, 50, fill="#E5E7EB", outline="#D1D5DB", width=3)
        circle.create_text(30, 30, text=step_info.get("icon", "○"), font=("Segoe UI", 20))
        
        # Step label
        label = tk.Label(
            step_container,
            text=step_name,
            font=("Segoe UI", 10, "bold"),
            bg="#F8FAFC",
            fg="#6B7280"
        )
        label.pack(pady=(0, 5))
        
        # Step description
        desc_label = tk.Label(
            step_container,
            text=step_info.get("description", ""),
            font=("Segoe UI", 8),
            bg="#F8FAFC",
            fg="#9CA3AF",
            wraplength=150
        )
        desc_label.pack()
        
        # Date label (will be populated when active)
        date_label = tk.Label(
            step_container,
            text="",
            font=("Segoe UI", 8),
            bg="#F8FAFC",
            fg="#6B7280"
        )
        date_label.pack(pady=(5, 0))
        
        # Connector line to next step
        connector = None
        if index < total_steps - 1:
            connector = tk.Canvas(
                self.steps_frame,
                width=40,
                height=4,
                highlightthickness=0,
                bg="#F8FAFC"
            )
            connector.pack(side=tk.LEFT, padx=5)
            connector.create_line(0, 2, 40, 2, fill="#E5E7EB", width=3)
        
        return {
            'container': step_container,
            'circle': circle,
            'label': label,
            'desc_label': desc_label,
            'date_label': date_label,
            'connector': connector,
            'step_name': step_name,
            'color': step_info.get("color", "#6B7280"),
            'bg_color': step_info.get("bg_color", "#F3F4F6"),
            'icon': step_info.get("icon", "○")
        }
    
    def update_progress(self, claim_data: Dict[str, Any]):
        """Update progress tracker with claim data."""
        logger.debug(f"Progress tracker update_progress called with Status={claim_data.get('Status')}, FiledAt={claim_data.get('FiledAt')}, VerifiedAt={claim_data.get('VerifiedAt')}, SettledAt={claim_data.get('SettledAt')}")
        
        self.claim_data = claim_data
        current_status = claim_data.get('Status', 'Pending')
        logger.debug(f"Current status: {current_status}")
        
        # Update step indicators
        status_order = ["Pending", "Verified", "Settled"]
        current_index = status_order.index(current_status) if current_status in status_order else 0
        logger.debug(f"Current status index: {current_index}")
        
        for i, step in enumerate(self.steps):
            step_name = step['step_name']
            step_index = status_order.index(step_name) if step_name in status_order else -1
            
            if step_index <= current_index:
                # Active step - highlight
                logger.debug(f"Activating step: {step_name}")
                self._activate_step(step, claim_data)
            else:
                # Inactive step
                logger.debug(f"Deactivating step: {step_name}")
                self._deactivate_step(step)
        
        # Update timeline
        logger.debug("Updating timeline")
        self._update_timeline(claim_data)
        logger.debug("Progress tracker update complete")
    
    def _activate_step(self, step: Dict[str, Any], claim_data: Dict[str, Any]):
        """Activate a step (mark as completed/current)."""
        circle = step['circle']
        label = step['label']
        date_label = step['date_label']
        color = step['color']
        icon = step['icon']
        step_name = step['step_name']
        
        # Clear and redraw circle
        circle.delete("all")
        circle.create_oval(10, 10, 50, 50, fill=color, outline=color, width=3)
        circle.create_text(30, 30, text=icon, font=("Segoe UI", 20), fill="white")
        
        # Update label
        label.config(fg=color, font=("Segoe UI", 10, "bold"))
        
        # Update date
        date_str = self._get_step_date(step_name, claim_data)
        if date_str:
            date_label.config(text=date_str, fg=color)
        else:
            date_label.config(text="")
        
        # Update connector if exists
        if step['connector']:
            step['connector'].delete("all")
            step['connector'].create_line(0, 2, 40, 2, fill=color, width=3)
    
    def _deactivate_step(self, step: Dict[str, Any]):
        """Deactivate a step (mark as not reached)."""
        circle = step['circle']
        label = step['label']
        date_label = step['date_label']
        
        # Clear and redraw circle (gray)
        circle.delete("all")
        circle.create_oval(10, 10, 50, 50, fill="#E5E7EB", outline="#D1D5DB", width=3)
        circle.create_text(30, 30, text=step['icon'], font=("Segoe UI", 20))
        
        # Update label
        label.config(fg="#6B7280", font=("Segoe UI", 10))
        
        # Clear date
        date_label.config(text="")
        
        # Update connector if exists
        if step['connector']:
            step['connector'].delete("all")
            step['connector'].create_line(0, 2, 40, 2, fill="#E5E7EB", width=3)
    
    def _get_step_date(self, step_name: str, claim_data: Dict[str, Any]) -> Optional[str]:
        """Get the date for a specific step."""
        if step_name == "Pending":
            filed_at = claim_data.get('FiledAt') or claim_data.get('CreatedAt')
            if filed_at:
                date_str = str(filed_at)[:10] if len(str(filed_at)) > 10 else str(filed_at)
                return f"Filed: {date_str}"
        
        elif step_name == "Verified":
            verified_at = claim_data.get('VerifiedAt')
            if verified_at:
                date_str = str(verified_at)[:10] if len(str(verified_at)) > 10 else str(verified_at)
                return f"Verified: {date_str}"
        
        elif step_name == "Settled":
            settled_at = claim_data.get('SettledAt')
            if settled_at:
                date_str = str(settled_at)[:10] if len(str(settled_at)) > 10 else str(settled_at)
                return f"Settled: {date_str}"
        
        return None
    
    def _update_timeline(self, claim_data: Dict[str, Any]):
        """Update timeline section with detailed dates."""
        # Clear existing timeline
        for widget in self.timeline_content.winfo_children():
            widget.destroy()
        
        # Timeline items
        timeline_items = []
        
        # Filed date
        filed_at = claim_data.get('FiledAt') or claim_data.get('CreatedAt')
        if filed_at:
            date_str = str(filed_at)[:10] if len(str(filed_at)) > 10 else str(filed_at)
            timeline_items.append({
                'date': date_str,
                'event': 'Claim Filed',
                'status': 'Pending',
                'icon': '📋'
            })
        
        # Verified date
        verified_at = claim_data.get('VerifiedAt')
        if verified_at:
            date_str = str(verified_at)[:10] if len(str(verified_at)) > 10 else str(verified_at)
            timeline_items.append({
                'date': date_str,
                'event': 'Claim Verified',
                'status': 'Verified',
                'icon': '✅'
            })
        
        # Settled date
        settled_at = claim_data.get('SettledAt')
        if settled_at:
            date_str = str(settled_at)[:10] if len(str(settled_at)) > 10 else str(settled_at)
            timeline_items.append({
                'date': date_str,
                'event': 'Claim Settled',
                'status': 'Settled',
                'icon': '✔️'
            })
        
        # Display timeline items
        if timeline_items:
            for item in timeline_items:
                self._create_timeline_item(item)
        else:
            ttk.Label(
                self.timeline_content,
                text="No timeline data available",
                foreground="#9CA3AF"
            ).pack(anchor=tk.W)
    
    def _create_timeline_item(self, item: Dict[str, Any]):
        """Create a timeline item."""
        item_frame = tk.Frame(self.timeline_content, bg=WHITE, relief="solid", borderwidth=1)
        item_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Icon and event
        left_frame = tk.Frame(item_frame, bg=WHITE)
        left_frame.pack(side=tk.LEFT, padx=10, pady=8)
        
        icon_label = tk.Label(
            left_frame,
            text=item['icon'],
            font=("Segoe UI", 16),
            bg=WHITE
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        event_label = tk.Label(
            left_frame,
            text=item['event'],
            font=("Segoe UI", 10, "bold"),
            bg=WHITE,
            fg=BLUE_PRIMARY
        )
        event_label.pack(side=tk.LEFT)
        
        # Date
        date_label = tk.Label(
            item_frame,
            text=item['date'],
            font=("Segoe UI", 9),
            bg=WHITE,
            fg=GRAY_TEXT
        )
        date_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Status badge
        status_frame = tk.Frame(item_frame, bg=WHITE)
        status_frame.pack(side=tk.RIGHT, padx=10)
        StatusBadge.create(status_frame, item['status'], row=0, column=0)

