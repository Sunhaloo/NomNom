"""
Deliveries page - shows your orders being delivered
"""

import flet as ft
from deliveries.deliveries_service import DeliveriesService
from deliveries.screens.map_screen import MapScreen
from common.error_handler import get_user_friendly_message, NetworkError
from common.formatters import calculate_distance_km, format_distance, get_status_color
from config import SHOP_LATITUDE, SHOP_LONGITUDE


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
        self.page_bg = "#E8DBC7"
        self.orange = "#FF9800"
        self.green = "#4CAF50"
        self.red = "#F44336"
        self.content_width = 380
        
        # Delivery lists by status
        self.pending_deliveries = []
        self.confirmed_deliveries = []
        self.canceled_deliveries = []

        self.map_screen = None
        
        # UI containers for each status section
        self.pending_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            controls=[],
        )
        self.confirmed_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            controls=[],
        )
        self.canceled_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.ALWAYS,
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

    def _wrap(self, control: ft.Control, *, expand: bool = False) -> ft.Row:
        """Keep content centered with a consistent max width."""
        return ft.Row(
            expand=expand,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=self.content_width,
                    content=control,
                )
            ],
        )
    
    def _create_delivery_item(self, delivery: dict, status_type: str) -> ft.Container:
        """Build a single delivery card for the list"""
        delivery_id = delivery.get("id", "N/A")
        status = delivery.get("status", "pending").replace("_", " ").title()
        address = delivery.get("address", "N/A")
        
        # Parse delivery date if available (format: "YYYY-MM-DD")
        delivery_date = delivery.get("date", "N/A")
        
        # For now, show distance to shop location
        # In a real scenario, this would be the distance to the delivery address
        distance_km = 2.5  # Placeholder - would need actual address parsing
        distance_display = format_distance(distance_km)
        
        # Brown-tone status color (theme-aligned)
        card_color = get_status_color(status_type, "delivery")

        # Light backgrounds to keep contrast while staying on-theme
        card_bg_color = {
            "Pending": "#F3E5DC",
            "Done": "#EFEBE9",
            "Cancelled": "#F5F0EE",
        }.get(status_type, self.lighter_brown)
        
        # Only show confirm button for pending deliveries
        show_confirm_btn = status_type == "Pending"
        
        return ft.Container(
            bgcolor=card_bg_color,
            border_radius=10,
            padding=12,
            border=ft.Border.all(2, card_color),
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
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
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
                        f"Distance: {distance_display}",
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
                                ft.FilledButton(
                                    content=ft.Text("Cancel", size=11),
                                    bgcolor=self.red,
                                    color=self.white,
                                    height=36,
                                    expand=True,
                                    on_click=lambda e, did=delivery_id: self._on_cancel_click(did),
                                ),
                                ft.FilledButton(
                                    content=ft.Text("My", size=11),
                                    bgcolor=self.primary_brown,
                                    color=self.white,
                                    height=36,
                                    on_click=lambda e, addr=address: self._on_my_button_click(addr),
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
        try:
            if self.loading.page:
                self.loading.update()
        except Exception:
            pass
        
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
            try:
                if self.loading.page:
                    self.loading.update()
            except Exception:
                pass
    
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
        """Handle confirming a pending delivery and syncing with DB"""
        # Update local data for immediate feedback
        target_delivery = None
        for i, d in enumerate(self.pending_deliveries):
            if str(d.get("id")) == str(delivery_id):
                target_delivery = self.pending_deliveries.pop(i)
                break
        
        if not target_delivery:
            return

        target_delivery["status"] = "Done"
        self.confirmed_deliveries.insert(0, target_delivery)
        self._update_all_lists()

        # Sync with backend/database
        try:
            self.deliveries_service.update_delivery_status(delivery_id, "Done")
            self.show_notification(f"Delivery #{delivery_id} confirmed successfully!")
        except Exception as e:
            # Revert local state if DB update fails
            target_delivery["status"] = "Pending"
            self.pending_deliveries.insert(0, target_delivery)
            self.confirmed_deliveries.remove(target_delivery)
            self._update_all_lists()
            self.show_notification(f"Failed to sync with database: {str(e)}", error=True)
    
    def _on_cancel_click(self, delivery_id):
        """Handle cancelling a pending delivery and syncing with DB"""
        target_delivery = None
        for i, d in enumerate(self.pending_deliveries):
            if str(d.get("id")) == str(delivery_id):
                target_delivery = self.pending_deliveries.pop(i)
                break
        
        if not target_delivery:
            return

        # Local update for immediate feedback
        target_delivery["status"] = "Cancelled"
        self.canceled_deliveries.insert(0, target_delivery)
        self._update_all_lists()

        # Sync with backend
        try:
            self.deliveries_service.update_delivery_status(delivery_id, "Cancelled")
            self.show_notification(f"Delivery #{delivery_id} cancelled.")
        except Exception as e:
            # Revert
            target_delivery["status"] = "Pending"
            self.pending_deliveries.insert(0, target_delivery)
            self.canceled_deliveries.remove(target_delivery)
            self._update_all_lists()
            self.show_notification(f"Failed to cancel in database: {str(e)}", error=True)

    def _on_my_button_click(self, delivery_address):
        """Handle 'My' button click - focus map on customer location."""
        if delivery_address:
            self.show_notification(f"Delivery to: {delivery_address}")
        if self.map_screen:
            self.map_screen.request_customer_location()
    
    def _on_map_click(self, delivery_id):
        """Handle map button click"""
        # Map is already visible on the page
        pass
    

    def build(self, page: ft.Page = None) -> ft.Container:
        """Create the deliveries screen UI"""
        self._load_deliveries()
        
        # Create map component with page reference
        self.map_screen = MapScreen(on_back=None)
        
        def create_status_section(title: str, deliveries_list) -> ft.Container:
            """Create a scrollable section for a delivery status"""
            return self._wrap(
                ft.Container(
                    height=250,
                    bgcolor=self.white,
                    border_radius=12,
                    padding=ft.Padding.symmetric(horizontal=15),
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
            )

        
        return ft.Container(
            expand=True,
            bgcolor=self.page_bg,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Fixed Header - NOT scrollable
                    ft.Container(
                        height=60,
                        padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                        content=self._wrap(
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Image(
                                        src="NomNom-Logo-mark.png",
                                        width=56,
                                        height=56,
                                        fit=ft.BoxFit.CONTAIN,
                                    ),
                                    ft.Text(
                                        "Deliveries",
                                        size=24,
                                        weight="bold",
                                        color=self.text_dark,
                                    ),
                                ],
                            )
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
                                self._wrap(
                                    ft.Container(
                                        height=250,
                                        content=self.map_screen.build(page=page),
                                    )
                                ),
                                
                                ft.Container(height=15),
                                
                                # Pending Deliveries
                                create_status_section("Pending Deliveries", self.pending_list),
                                ft.Container(height=15),
                                
                                # Confirmed Deliveries
                                create_status_section("Confirmed Deliveries", self.confirmed_list),
                                ft.Container(height=15),
                                
                                # Canceled Deliveries
                                create_status_section("Canceled Deliveries", self.canceled_list),
                                ft.Container(height=90),
                            ],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )
