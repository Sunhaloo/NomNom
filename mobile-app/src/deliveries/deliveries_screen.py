"""
Deliveries page - shows your orders being delivered
"""

import flet as ft
import datetime
from deliveries.deliveries_service import DeliveriesService
from deliveries.screens.map_screen import MapScreen
from common.error_handler import get_user_friendly_message, NetworkError


class DeliveriesScreen:
    """Shows deliveries with map and status sections"""
    
    def __init__(self, deliveries_service: DeliveriesService, show_notification):
        """Set up the deliveries page"""
        self.deliveries_service = deliveries_service
        self.show_notification = show_notification
        
        # Colors
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        self.orange = "#FF9800"
        self.green = "#4CAF50"
        self.red = "#F44336"
        
        # Delivery lists by status
        self.pending_deliveries = []
        self.confirmed_deliveries = []
        self.canceled_deliveries = []
        
        # UI containers for each status section
        self.pending_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[],
        )
        self.confirmed_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[],
        )
        self.canceled_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[],
        )
        
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)

    def _safe_update(self, control: ft.Control) -> None:
        """Update a control if it is attached to the page."""
        try:
            control.update()
        except RuntimeError:
            # Control not yet added to page
            pass
    
    def _create_delivery_item(self, delivery: dict, status_type: str) -> ft.Container:
        """Build a single delivery card for the list"""
        delivery_id = delivery.get("id", "N/A")
        status = delivery.get("status", "pending").replace("_", " ").title()
        address = delivery.get("address", "N/A")
        estimated_eta = delivery.get("estimated_eta", "N/A")
        
        # Card color based on status type
        card_color = {
            "Pending": self.orange,
            "Done": self.green,
            "Cancelled": self.red,
        }.get(status_type, self.lighter_brown)
        
        # Light version of the card color for background
        card_bg_color = {
            "Pending": "#FFF3E0",
            "Done": "#E8F5E9",
            "Cancelled": "#FFEBEE",
        }.get(status_type, self.lighter_brown)
        
        # Only show confirm button for pending deliveries
        show_confirm_btn = status_type == "Pending"
        
        return ft.Container(
            bgcolor=card_bg_color,
            border_radius=10,
            padding=12,
            border=ft.border.all(2, card_color),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"Delivery #{delivery_id}",
                                size=13,
                                weight="bold",
                                color=self.text_dark,
                            ),
                            ft.Container(
                                bgcolor=card_color,
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                content=ft.Text(
                                    status_type.title(),
                                    size=10,
                                    color=self.white,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Address: {address}",
                        size=11,
                        color=self.text_light,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"ETA: {estimated_eta}",
                        size=10,
                        color=self.text_light,
                    ),
                    ft.Text(
                        self._format_status_timestamp(delivery),
                        size=9,
                        color=self.text_light,
                        italic=True,
                    ),
                    
                    # Action buttons (only for pending)
                    ft.Container(
                        visible=show_confirm_btn,
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.FilledButton(
                                    content=ft.Text("Confirm", size=11),
                                    bgcolor=self.primary_brown,
                                    color=self.white,
                                    height=36,
                                    expand=True,
                                    on_click=lambda e, did=delivery_id: self._on_confirm_click(did),
                                ),
                                ft.FilledButton(
                                    content=ft.Text("Cancel", size=11),
                                    bgcolor=self.red,
                                    color=self.white,
                                    height=36,
                                    expand=True,
                                    on_click=lambda e, did=delivery_id: self._on_cancel_click(did),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.MAP,
                                    icon_color=self.primary_brown,
                                    icon_size=18,
                                    on_click=lambda e, did=delivery_id: self._on_map_click(did),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
    
    def _load_deliveries(self):
        """Fetch all deliveries from service"""
        self.loading.visible = True
        self._safe_update(self.loading)
        try:
            # Fetch pending deliveries
            pending_result = self.deliveries_service.get_deliveries(
                status="Pending",
                limit=50,
            )
            self.pending_deliveries = pending_result.get("results", [])
            
            # Fetch done/confirmed deliveries
            in_transit_result = self.deliveries_service.get_deliveries(
                status="Done",
                limit=50,
            )
            self.confirmed_deliveries = in_transit_result.get("results", [])
            
            # Fetch cancelled deliveries
            cancelled_result = self.deliveries_service.get_deliveries(
                status="Cancelled",
                limit=50,
            )
            self.canceled_deliveries = cancelled_result.get("results", [])
            
            self._update_all_lists()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.loading.visible = False
            self._safe_update(self.loading)
    
    def _update_all_lists(self):
        """Refresh all delivery list displays"""
        self._update_list(self.pending_list, self.pending_deliveries, "Pending")
        self._update_list(self.confirmed_list, self.confirmed_deliveries, "Done")
        self._update_list(self.canceled_list, self.canceled_deliveries, "Cancelled")
    
    def _update_list(self, list_container, deliveries, status_type):
        """Update a specific delivery list display"""
        if not deliveries:
            list_container.controls = [
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=40,
                    content=ft.Text(
                        f"No {status_type} deliveries",
                        size=12,
                        color=self.text_light,
                    ),
                ),
            ]
        else:
            list_container.controls = [
                self._create_delivery_item(delivery, status_type) for delivery in deliveries
            ]
        
        self._safe_update(list_container)
    
    def _on_confirm_click(self, delivery_id):
        """Handle confirming a pending delivery without photo"""
        # Record confirmation timestamp
        now = datetime.datetime.now().isoformat()
        # Update local data
        for d in self.pending_deliveries:
            if d.get("id") == delivery_id:
                d["status"] = "Done"
                d["confirmed_at"] = now
                self.confirmed_deliveries.insert(0, d)
                self.pending_deliveries.remove(d)
                break
        # Optionally call backend (placeholder)
        try:
            self.deliveries_service.update_delivery_status(delivery_id, "Done")
        except Exception:
            pass  # ignore if method not implemented
        # Refresh UI lists
        self._update_all_lists()
    
    def _on_cancel_click(self, delivery_id):
        """Handle cancelling a pending delivery"""
        now = datetime.datetime.now().isoformat()
        for d in self.pending_deliveries:
            if d.get("id") == delivery_id:
                d["status"] = "Cancelled"
                d["canceled_at"] = now
                self.canceled_deliveries.insert(0, d)
                self.pending_deliveries.remove(d)
                break
        try:
            self.deliveries_service.update_delivery_status(delivery_id, "Cancelled")
        except Exception:
            pass
        self._update_all_lists()

    def _format_status_timestamp(self, delivery: dict) -> str:
        """Return a formatted status timestamp string for a delivery.
        Uses ISO format stored in `confirmed_at` or `canceled_at`.
        Returns empty string if no timestamp is present.
        """
        ts = delivery.get("confirmed_at") or delivery.get("canceled_at")
        if not ts:
            return ""
        try:
            dt = datetime.datetime.fromisoformat(ts)
        except Exception:
            try:
                dt = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f%z")
            except Exception:
                return ""
        status = "confirmed" if "confirmed_at" in delivery else "cancelled"
        formatted = dt.strftime("%d %B %Y at %H:%M")
        return f"Delivery {status} on {formatted}"

    
    def build(self, page: ft.Page = None) -> ft.Container:
        """Create the deliveries screen UI"""
        if page:
            page.scrollbar_theme = ft.ScrollbarTheme(
                thumb_color=self.primary_brown,
                thickness=10,
                radius=10,
                main_axis_margin=2,
                thumb_visibility=True,
            )
        
        self._load_deliveries()
        
        # Create map component with page reference
        map_screen = MapScreen(on_back=None)
        
        def create_status_section(title: str, deliveries_list) -> ft.Container:
            """Create a scrollable section for a delivery status"""
            return ft.Container(
                height=250,
                bgcolor=self.white,
                padding=ft.padding.symmetric(horizontal=15),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            title,
                            size=16,
                            weight="bold",
                            color=self.text_dark,
                        ),
                        ft.Container(height=8),
                        deliveries_list,
                    ],
                    spacing=0,
                ),
            )

        
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                controls=[
                    # Fixed Header - NOT scrollable
                    ft.Container(
                        height=60,
                        padding=ft.padding.symmetric(horizontal=20, vertical=15),
                        content=ft.Text(
                            "Deliveries",
                            size=24,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    # Everything below is scrollable
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            controls=[
                                ft.Container(height=15),
                                
                                # Map section
                                ft.Container(
                                    height=250,
                                    padding=ft.padding.symmetric(horizontal=15),
                                    content=map_screen.build(page=page),
                                ),
                                
                                ft.Container(height=15),
                                
                                # Pending Deliveries
                                create_status_section(
                                    "Pending Deliveries",
                                    self.pending_list
                                ),
                                ft.Container(height=15),
                                
                                # Confirmed Deliveries
                                create_status_section(
                                    "Confirmed Deliveries",
                                    self.confirmed_list
                                ),
                                ft.Container(height=15),
                                
                                # Canceled Deliveries
                                create_status_section(
                                    "Canceled Deliveries",
                                    self.canceled_list
                                ),
                                ft.Container(height=20),
                            ],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )
