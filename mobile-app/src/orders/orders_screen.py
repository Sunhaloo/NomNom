"""
Orders screen for the NomNom mobile app.
Displays list of user orders with filtering.
"""

import flet as ft
from orders.orders_service import OrdersService
from common.error_handler import get_user_friendly_message, NetworkError


class OrdersScreen:
    """Orders screen with list and filtering."""
    
    def __init__(self, orders_service: OrdersService, show_notification):
        """
        Initialize orders screen.
        
        Args:
            orders_service: OrdersService instance
            show_notification: Function to show notifications
        """
        self.orders_service = orders_service
        self.show_notification = show_notification
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        
        # Data
        self.orders = []
        self.current_status_filter = None
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)
        
        # Search field
        self.search_field = ft.TextField(
            label="Search Order ID",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
            on_change=self._on_search_change,
        )
        
        # Filter buttons
        self.filter_buttons = ft.Row(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Orders list
        self.orders_list = ft.Column(
            spacing=10,
            controls=[],
        )
    
    def _create_filter_buttons(self):
        """Create filter button row."""
        statuses = [
            ("All", None),
            ("Pending", "pending"),
            ("Processing", "processing"),
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
        self._load_orders()
        self.filter_buttons.update()
    
    def _create_order_item(self, order: dict) -> ft.Container:
        """Create an order list item."""
        order_id = order.get("id", "N/A")
        status = order.get("status", "pending").title()
        total = order.get("total_amount", 0)
        order_date = order.get("created_at", "N/A")
        
        status_color = {
            "Pending": "#FF9800",
            "Processing": "#2196F3",
            "Delivered": "#4CAF50",
            "Cancelled": "#F44336",
        }.get(status, self.text_light)
        
        return ft.Container(
            bgcolor=self.lighter_brown,
            border_radius=10,
            padding=15,
            on_click=lambda e: self._on_order_click(order_id),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"Order #{order_id}",
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
                        f"Total: ${total:.2f}",
                        size=12,
                        color=self.text_light,
                    ),
                    ft.Text(
                        f"Date: {order_date}",
                        size=11,
                        color=self.text_light,
                    ),
                ],
            ),
        )
    
    def _load_orders(self):
        """Load orders from service."""
        self.loading.visible = True
        self.loading.update()
        
        try:
            result = self.orders_service.get_orders(
                status=self.current_status_filter,
                limit=50,
            )
            self.orders = result.get("results", [])
            self._update_orders_list()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.loading.visible = False
            self.loading.update()
    
    def _update_orders_list(self):
        """Update orders list display."""
        if not self.orders:
            self.orders_list.controls = [
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=40,
                    content=ft.Text(
                        "No orders found",
                        size=14,
                        color=self.text_light,
                    ),
                ),
            ]
        else:
            self.orders_list.controls = [
                self._create_order_item(order) for order in self.orders
            ]
        
        self.orders_list.update()
    
    def _on_search_change(self, e):
        """Handle search field change."""
        # Can be enhanced with debouncing later
        pass
    
    def _on_order_click(self, order_id):
        """Handle order item click."""
        # Navigate to order detail screen
        pass
    
    def build(self) -> ft.Container:
        """Build and return orders screen UI."""
        self._create_filter_buttons()
        self._load_orders()
        
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
                            "Orders",
                            size=24,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Search field
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15),
                        content=self.search_field,
                    ),
                    
                    ft.Container(height=10),
                    
                    # Filter buttons
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15),
                        content=self.filter_buttons,
                    ),
                    
                    ft.Container(height=15),
                    
                    # Loading indicator
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=self.loading,
                    ),
                    
                    # Orders list
                    ft.Container(
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=15),
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[self.orders_list],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )
