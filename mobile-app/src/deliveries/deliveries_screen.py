"""
Deliveries screen for the NomNom mobile app.
Displays list of deliveries with status filtering and confirmation action.
"""

import flet as ft
from deliveries.deliveries_service import DeliveriesService
from common.error_handler import get_user_friendly_message, NetworkError


class DeliveriesScreen:
    """Deliveries screen with list and status filtering."""
    
    def __init__(self, deliveries_service: DeliveriesService, show_notification):
        """
        Initialize deliveries screen.
        
        Args:
            deliveries_service: DeliveriesService instance
            show_notification: Function to show notifications
        """
        self.deliveries_service = deliveries_service
        self.show_notification = show_notification
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        
        # Data
        self.deliveries = []
        self.current_status_filter = None
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)
        
        # Filter buttons
        self.filter_buttons = ft.Row(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Deliveries list
        self.deliveries_list = ft.Column(
            spacing=10,
            controls=[],
        )
    
    def _create_filter_buttons(self):
        """Create filter button row."""
        statuses = [
            ("All", None),
            ("Pending", "pending"),
            ("In Transit", "in_transit"),
            ("Delivered", "delivered"),
            ("Cancelled", "cancelled"),
        ]
        
        buttons = []
        for label, status in statuses:
            buttons.append(
                ft.FilledButton(
                    content=ft.Text(label),
                    bgcolor=self.primary_brown if status == self.current_status_filter else self.lighter_brown,
                    color=self.white if status == self.current_status_filter else self.text_dark,
                    on_click=lambda e, s=status: self._apply_filter(s),
                )
            )
        
        self.filter_buttons.controls = buttons
    
    def _apply_filter(self, status: str | None):
        """Apply status filter."""
        self.current_status_filter = status
        self._create_filter_buttons()
        self._load_deliveries()
        self.filter_buttons.update()
    
    def _create_delivery_item(self, delivery: dict) -> ft.Container:
        """Create a delivery list item."""
        delivery_id = delivery.get("id", "N/A")
        status = delivery.get("status", "pending").replace("_", " ").title()
        address = delivery.get("delivery_address", "N/A")
        estimated_eta = delivery.get("estimated_eta", "N/A")
        
        status_color = {
            "Pending": "#FF9800",
            "In Transit": "#2196F3",
            "Delivered": "#4CAF50",
            "Cancelled": "#F44336",
        }.get(status, self.text_light)
        
        # Show confirm button only for pending deliveries
        show_confirm_btn = status.lower() == "pending" or status.lower() == "in transit"
        
        return ft.Container(
            bgcolor=self.lighter_brown,
            border_radius=10,
            padding=15,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"Delivery #{delivery_id}",
                                size=14,
                                weight="bold",
                                color=self.text_dark,
                            ),
                            ft.Container(
                                bgcolor=status_color,
                                border_radius=5,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                content=ft.Text(
                                    status,
                                    size=11,
                                    color=self.white,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Address: {address}",
                        size=12,
                        color=self.text_light,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"ETA: {estimated_eta}",
                        size=11,
                        color=self.text_light,
                    ),
                    
                    # Confirm button (visible only for pending/in-transit)
                    ft.Container(
                        visible=show_confirm_btn,
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                ft.FilledButton(
                                    content=ft.Text("Confirm with Photo"),
                                    bgcolor=self.primary_brown,
                                    color=self.white,
                                    height=40,
                                    expand=True,
                                    on_click=lambda e, did=delivery_id: self._on_confirm_click(did),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.MAP,
                                    icon_color=self.primary_brown,
                                    on_click=lambda e, did=delivery_id: self._on_map_click(did),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
    
    def _load_deliveries(self):
        """Load deliveries from service."""
        self.loading.visible = True
        self.loading.update()
        
        try:
            result = self.deliveries_service.get_deliveries(
                status=self.current_status_filter,
                limit=50,
            )
            self.deliveries = result.get("results", [])
            self._update_deliveries_list()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.loading.visible = False
            self.loading.update()
    
    def _update_deliveries_list(self):
        """Update deliveries list display."""
        if not self.deliveries:
            self.deliveries_list.controls = [
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=40,
                    content=ft.Text(
                        "No deliveries found",
                        size=14,
                        color=self.text_light,
                    ),
                ),
            ]
        else:
            self.deliveries_list.controls = [
                self._create_delivery_item(delivery) for delivery in self.deliveries
            ]
        
        self.deliveries_list.update()
    
    def _on_confirm_click(self, delivery_id):
        """Handle confirm delivery click."""
        # Navigate to delivery confirmation screen with camera
        pass
    
    def _on_map_click(self, delivery_id):
        """Handle map/location click."""
        # Open map or show delivery location
        pass
    
    def build(self) -> ft.Container:
        """Build and return deliveries screen UI."""
        self._create_filter_buttons()
        self._load_deliveries()
        
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(height=15),
                    
                    # Header
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Text(
                            "Deliveries",
                            size=24,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Filter buttons
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15),
                        content=self.filter_buttons,
                    ),
                    
                    ft.Container(height=15),
                    
                    # Loading indicator
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=self.loading,
                    ),
                    
                    # Deliveries list
                    ft.Container(
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=15),
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[self.deliveries_list],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )
