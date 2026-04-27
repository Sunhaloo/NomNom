"""
Deliveries page - shows your orders being delivered
"""

import flet as ft
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
            controls=[],
        )
        self.confirmed_list = ft.Column(
            spacing=10,
            controls=[],
        )
        self.canceled_list = ft.Column(
            spacing=10,
            controls=[],
        )
        
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)

    
    def _create_delivery_item(self, delivery: dict, status_type: str) -> ft.Container:
        """Build a single delivery card for the list"""
        delivery_id = delivery.get("id", "N/A")
        status = delivery.get("status", "pending").replace("_", " ").title()
        address = delivery.get("delivery_address", "N/A")
        estimated_eta = delivery.get("estimated_eta", "N/A")
        
        # Card color based on status type
        card_color = {
            "pending": self.orange,
            "confirmed": self.green,
            "canceled": self.red,
        }.get(status_type.lower(), self.lighter_brown)
        
        # Light version of the card color for background
        card_bg_color = {
            "pending": "#FFF3E0",
            "confirmed": "#E8F5E9",
            "canceled": "#FFEBEE",
        }.get(status_type.lower(), self.lighter_brown)
        
        # Only show confirm button for pending deliveries
        show_confirm_btn = status_type.lower() == "pending"
        
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
        """Fetch deliveries from the API for all statuses"""
        self.loading.visible = True
        
        try:
            # Fetch pending deliveries
            pending_result = self.deliveries_service.get_deliveries(
                status="pending",
                limit=50,
            )
            self.pending_deliveries = pending_result.get("results", [])
            
            # Fetch confirmed deliveries
            confirmed_result = self.deliveries_service.get_deliveries(
                status="in_transit",
                limit=50,
            )
            self.confirmed_deliveries = confirmed_result.get("results", [])
            
            # Fetch canceled deliveries
            canceled_result = self.deliveries_service.get_deliveries(
                status="cancelled",
                limit=50,
            )
            self.canceled_deliveries = canceled_result.get("results", [])
            
            self._update_all_lists()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.loading.visible = False
    
    def _update_all_lists(self):
        """Refresh all delivery list displays"""
        self._update_list(self.pending_list, self.pending_deliveries, "pending")
        self._update_list(self.confirmed_list, self.confirmed_deliveries, "confirmed")
        self._update_list(self.canceled_list, self.canceled_deliveries, "canceled")
    
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
        
        list_container.update()
    
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
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                expand=True,
                                scroll=ft.ScrollMode.AUTO,
                                spacing=10,
                                controls=[deliveries_list],
                            ),
                        ),
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
