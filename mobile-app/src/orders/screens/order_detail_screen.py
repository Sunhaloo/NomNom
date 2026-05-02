"""
Order Detail screen for the NomNom mobile app.
Displays full itemized order receipt with pastries, pricing breakdown, and delivery info.
"""

import flet as ft
from orders.orders_service import OrdersService
from common.error_handler import get_user_friendly_message, NetworkError
from common.formatters import format_currency, format_date, format_delivery_status, get_status_color


class OrderDetailScreen:
    """Order detail screen with itemized receipt."""
    
    def __init__(self, orders_service: OrdersService, show_notification, on_back=None):
        """
        Initialize order detail screen.
        
        Args:
            orders_service: OrdersService instance
            show_notification: Function to show notifications
            on_back: Callback for back button
        """
        self.orders_service = orders_service
        self.show_notification = show_notification
        self.on_back = on_back
        self.order = {}
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        self.success_green = "#4CAF50"
        self.warning_orange = "#FF9800"
        self.error_red = "#F44336"
        self.content_width = 380
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown)
        
        # Content container
        self.content_column = ft.Column(visible=False)

    def _wrap(self, control: ft.Control, *, expand: bool = False) -> ft.Container:
        """Keep content centered with a consistent max width."""
        return ft.Container(
            width=self.content_width,
            alignment=ft.Alignment.TOP_CENTER,
            expand=expand,
            content=control,
        )
    
    def _create_pastry_item(self, item: dict) -> ft.Container:
        """Create a pastry item row for the receipt."""
        pastry_name = item.get("pastry_name", "Unknown Pastry")
        quantity = item.get("quantity", 1)
        price = item.get("price", "0.00")
        subtotal = item.get("subtotal", "0.00")
        
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                pastry_name,
                                size=13,
                                color=self.text_dark,
                                weight="w500",
                            ),
                            ft.Text(
                                format_currency(subtotal),
                                size=13,
                                color=self.text_dark,
                                weight="w500",
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"Qty: {quantity} x {format_currency(price)}",
                                size=11,
                                color=self.text_light,
                            ),
                        ],
                    ),
                ],
            ),
        )
    
    def _create_pricing_breakdown(self) -> ft.Column:
        """Create pricing breakdown section."""
        subtotal = self._calculate_subtotal()
        tax = self.order.get("tax_amount", "0.00")
        delivery_fee = self.order.get("delivery_fee", "0.00")
        total = self.order.get("total_amount", "0.00")
        
        return ft.Column(
            spacing=0,
            controls=[
                # Subtotal
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Subtotal", size=12, color=self.text_light),
                            ft.Text(format_currency(subtotal), size=12, color=self.text_light),
                        ],
                    ),
                ),
                # Tax
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Tax", size=12, color=self.text_light),
                            ft.Text(format_currency(tax), size=12, color=self.text_light),
                        ],
                    ),
                ),
                # Delivery Fee
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=15, vertical=8),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Delivery Fee", size=12, color=self.text_light),
                            ft.Text(format_currency(delivery_fee), size=12, color=self.text_light),
                        ],
                    ),
                ),
                # Divider
                ft.Divider(height=1, color=self.lighter_brown),
                # Total
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=15, vertical=12),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Total",
                                size=14,
                                weight="bold",
                                color=self.text_dark,
                            ),
                            ft.Text(
                                format_currency(total),
                                size=14,
                                weight="bold",
                                color=self.primary_brown,
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    def _calculate_subtotal(self) -> float:
        """Calculate subtotal from items."""
        items = self.order.get("items", [])
        subtotal = 0.0
        for item in items:
            try:
                subtotal += float(item.get("subtotal", 0))
            except (ValueError, TypeError):
                pass
        return subtotal
    
    def _create_delivery_info(self) -> ft.Container:
        """Create delivery information section."""
        delivery = self.order.get("delivery", {})
        
        if not delivery:
            return ft.Container(
                padding=15,
                content=ft.Text(
                    "No delivery information",
                    size=12,
                    color=self.text_light,
                ),
            )
        
        address = delivery.get("address", "N/A")
        status = delivery.get("status", "Unknown")
        date = delivery.get("date", "N/A")
        status_display = format_delivery_status(status)
        status_color = get_status_color(status, "delivery")
        
        return ft.Container(
            padding=15,
            bgcolor=self.lighter_brown,
            border_radius=10,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Delivery Info",
                                size=13,
                                weight="w500",
                                color=self.text_dark,
                            ),
                            ft.Container(
                                bgcolor=status_color,
                                border_radius=5,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                                content=ft.Text(
                                    status_display,
                                    size=11,
                                    color=self.white,
                                ),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        name=ft.Icons.LOCATION_ON,
                                        size=16,
                                        color=self.primary_brown,
                                    ),
                                    ft.Text(
                                        address,
                                        size=12,
                                        color=self.text_dark,
                                        expand=True,
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        name=ft.Icons.CALENDAR_TODAY,
                                        size=16,
                                        color=self.primary_brown,
                                    ),
                                    ft.Text(
                                        format_date(date),
                                        size=12,
                                        color=self.text_dark,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )
    
    def _load_order(self, order_id: int):
        """Load order details from service."""
        try:
            self.order = self.orders_service.get_order_detail(order_id)
            self._update_ui()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
    
    def _update_ui(self):
        """Update UI with loaded order data."""
        if not self.order:
            return
        
        order_id = self.order.get("id", "N/A")
        order_status = self.order.get("order_status", "Unknown")
        order_date = self.order.get("order_date", "N/A")
        items = self.order.get("items", [])
        
        status_display = format_delivery_status(order_status)
        status_color = get_status_color(order_status, "order")
        
        # Build items list
        items_controls = [
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                content=ft.Text(
                    "Order Items",
                    size=14,
                    weight="bold",
                    color=self.text_dark,
                ),
            ),
        ]
        
        if items:
            for item in items:
                items_controls.append(self._create_pastry_item(item))
        else:
            items_controls.append(
                ft.Container(
                    padding=15,
                    content=ft.Text(
                        "No items in this order",
                        size=12,
                        color=self.text_light,
                    ),
                )
            )
        
        # Build main content
        self.content_column.controls = [
            # Header with order ID and status
            ft.Container(
                padding=15,
                bgcolor=self.lighter_brown,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    f"Order #{order_id}",
                                    size=20,
                                    weight="bold",
                                    color=self.text_dark,
                                ),
                                ft.Container(
                                    bgcolor=status_color,
                                    border_radius=5,
                                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                                    content=ft.Text(
                                        status_display,
                                        size=12,
                                        color=self.white,
                                    ),
                                ),
                            ],
                        ),
                        ft.Text(
                            f"Order Date: {format_date(order_date)}",
                            size=12,
                            color=self.text_light,
                        ),
                    ],
                ),
            ),
            
            ft.Container(height=15),
            
            # Items section
            ft.Container(
                content=ft.Column(
                    spacing=0,
                    controls=items_controls,
                ),
            ),
            
            ft.Container(height=15),
            
            # Divider
            ft.Divider(height=1, color=self.lighter_brown),
            
            # Pricing breakdown
            self._create_pricing_breakdown(),
            
            ft.Container(height=15),
            
            # Delivery info
            ft.Container(
                padding=15,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(
                            "Delivery",
                            size=14,
                            weight="bold",
                            color=self.text_dark,
                        ),
                        self._create_delivery_info(),
                    ],
                ),
            ),
            
            ft.Container(height=20),
        ]
        self.content_column.visible = True
    
    def build(self, order_id: int) -> ft.Container:
        """Build and return order detail screen UI."""
        self._load_order(order_id)
        
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Header with back button
                    self._wrap(
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        icon_color=self.primary_brown,
                                        on_click=lambda e: self._on_back_click(),
                                    ),
                                    ft.Text(
                                        "Order Details",
                                        size=18,
                                        weight="bold",
                                        color=self.text_dark,
                                    ),
                                ],
                            ),
                        )
                    ),
                    
                    # Loading indicator
                    self._wrap(
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=self.loading,
                        )
                    ),
                    
                    # Scrollable content
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[self._wrap(self.content_column), ft.Container(height=90)],
                        ),
                    ),
                ],
                spacing=0,
            ),
        )
    
    def _on_back_click(self):
        """Handle back button click."""
        if self.on_back:
            self.on_back()
