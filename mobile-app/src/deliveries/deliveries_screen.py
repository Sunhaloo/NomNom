"""
Deliveries page - shows your orders being delivered
"""

import flet as ft
from deliveries.deliveries_service import DeliveriesService
from deliveries.screens.map_screen import MapScreen
from common.error_handler import get_user_friendly_message, NetworkError


class DeliveriesScreen:
    """Shows deliveries with filters and map"""
    
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
        
        self.deliveries = []
        self.current_status_filter = None
        
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)
        
        self.filter_buttons = ft.Row(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.deliveries_list = ft.Column(
            spacing=10,
            controls=[],
        )
    
    def _create_filter_buttons(self):
        """Create buttons for filtering deliveries by status"""
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
        """Filter deliveries by the selected status"""
        self.current_status_filter = status
        self._create_filter_buttons()
        self._load_deliveries()
        self.filter_buttons.update()
    
    def _create_delivery_item(self, delivery: dict) -> ft.Container:
        """Build a single delivery card for the list"""
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
        
        # Only show confirm button for active deliveries
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
                    
                    # Action buttons
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
        """Fetch deliveries from the API"""
        # Don't update during first build, control isn't on page yet
        self.loading.visible = True
        
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
    
    def _update_deliveries_list(self):
        """Refresh the delivery list display"""
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
        """Handle clicking confirm delivery button"""
        # Navigate to camera to take proof photo
        pass
    
    def _on_map_click(self, delivery_id):
        """Handle map button click"""
        # Map is already visible on the page
        pass
    
    def build(self, page: ft.Page = None) -> ft.Container:
        """Create the deliveries screen UI"""
        self._create_filter_buttons()
        self._load_deliveries()
        
        # Create map component with page reference
        map_screen = MapScreen(on_back=None)
        
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
                    
                    # Show map at top
                    ft.Container(
                        height=250,
                        padding=ft.padding.symmetric(horizontal=15),
                        content=map_screen.build(page=page),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Loading spinner
                    ft.Container(
                        content=self.loading,
                    ),
                    
                    # List of deliveries below
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
