"""
Orders screen for the NomNom mobile app.
Displays list of user orders with filtering.
"""

import flet as ft
from orders.orders_service import OrdersService
from common.error_handler import get_user_friendly_message, NetworkError
from common.formatters import (
    format_currency,
    format_date,
    format_delivery_status,
    format_order_status,
    get_status_color,
)


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

        # Selected order detail state (inline details panel)
        self.selected_order_id: int | None = None
        self.selected_order: dict | None = None
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown, visible=False)
        self.detail_loading = ft.ProgressRing(color=self.primary_brown, visible=False)
        
        # Order ID field (matches wireframe: "Details About Order" -> enter ID)
        self.order_id_field = ft.TextField(
            label="Order ID",
            hint_text="Enter order ID and press Enter",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=self._on_order_id_submit,
        )

        self.order_id_load_btn = ft.IconButton(
            icon=ft.Icons.SEARCH,
            icon_color=self.white,
            bgcolor=self.primary_brown,
            tooltip="Load order",
            on_click=self._on_order_id_load_click,
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

        # Inline order details panel body (updated dynamically)
        self.detail_panel_body = ft.Column(
            spacing=10,
            controls=[],
        )
        self._render_selected_order()

    def _safe_update(self, control: ft.Control) -> None:
        """Update a control if it is attached to the page."""
        try:
            control.update()
        except RuntimeError:
            # Control not yet added to page
            pass
    
    def _create_filter_buttons(self):
        """Create filter button row."""
        statuses = [
            ("All", None),
            ("Pending", "pending"),
            ("Paid", "paid"),
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
        status = order.get("order_status", "Pending")
        total = order.get("total_amount", "0.00")
        order_date = order.get("order_date", "")

        status_display = format_order_status(status)
        status_color = get_status_color(status, "order")
        
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
                                    status_display,
                                    size=11,
                                    color=self.white,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Total: {format_currency(total)}",
                        size=12,
                        color=self.text_light,
                    ),
                    ft.Text(
                        f"Date: {format_date(order_date, output_format='%b %d')}",
                        size=11,
                        color=self.text_light,
                    ),
                ],
            ),
        )
    
    def _load_orders(self):
        """Load orders from service."""
        self.loading.visible = True
        try:
            self.loading.update()
        except RuntimeError:
            # Control not yet added to page
            pass
        
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
            try:
                self.loading.update()
            except RuntimeError:
                # Control not yet added to page
                pass
    
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
        
        self._safe_update(self.orders_list)
    
    def _on_order_click(self, order_id):
        """Handle order item click."""
        self._select_order(order_id)

    def _on_order_id_submit(self, e):
        """Handle pressing Enter on the Order ID field."""
        self._select_order(self.order_id_field.value)

    def _on_order_id_load_click(self, e):
        """Handle clicking the load/search button next to the Order ID field."""
        self._select_order(self.order_id_field.value)

    def _parse_order_id(self, value) -> int | None:
        """Parse an order id from a value that may be int/str."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            text = str(value).strip()
            if not text:
                return None
            return int(text)
        except Exception:
            return None

    def _select_order(self, order_id):
        """Fetch and display order details in the inline panel."""
        parsed_id = self._parse_order_id(order_id)
        if parsed_id is None:
            self.show_notification("Please enter a valid numeric Order ID.", error=True)
            return

        self.selected_order_id = parsed_id
        self.selected_order = None

        # Keep the field in sync when user taps a card
        self.order_id_field.value = str(parsed_id)
        self._safe_update(self.order_id_field)

        self.detail_loading.visible = True
        self._safe_update(self.detail_loading)

        try:
            self.selected_order = self.orders_service.get_order_detail(parsed_id)
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
            self.selected_order = None
        finally:
            self.detail_loading.visible = False
            self._safe_update(self.detail_loading)

        self._render_selected_order()

    def _money_to_float(self, value) -> float:
        """Best-effort conversion of money strings to float."""
        try:
            if value is None:
                return 0.0
            return float(value)
        except Exception:
            return 0.0

    def _render_selected_order(self):
        """Render the inline order details panel."""
        if not self.selected_order_id:
            self.detail_panel_body.controls = [
                ft.Text(
                    "Select an order to see details.",
                    size=12,
                    color=self.text_light,
                )
            ]
            self._safe_update(self.detail_panel_body)
            return

        if not self.selected_order:
            self.detail_panel_body.controls = [
                ft.Text(
                    f"Couldn’t load order #{self.selected_order_id}.",
                    size=12,
                    color=self.text_light,
                )
            ]
            self._safe_update(self.detail_panel_body)
            return

        order = self.selected_order
        order_id = order.get("id", self.selected_order_id)
        order_status = order.get("order_status", "")
        order_date = order.get("order_date", "")
        items = order.get("items", []) or []

        status_display = format_order_status(order_status)
        status_color = get_status_color(order_status, "order")

        # Totals
        subtotal_value = 0.0
        for item in items:
            if isinstance(item, dict):
                if "subtotal" in item:
                    subtotal_value += self._money_to_float(item.get("subtotal"))
                else:
                    qty = self._money_to_float(item.get("quantity"))
                    price = self._money_to_float(item.get("price"))
                    subtotal_value += qty * price

        tax = order.get("tax_amount", "0.00")
        delivery_fee = order.get("delivery_fee", "0.00")
        total = order.get("total_amount", "0.00")

        # Items list (scrollable)
        item_controls: list[ft.Control] = []
        if items:
            for item in items:
                if not isinstance(item, dict):
                    continue
                pastry_name = item.get("pastry_name", "Unknown")
                quantity = item.get("quantity", 0)
                price = item.get("price", "0.00")
                line_subtotal = item.get("subtotal", None)

                item_controls.append(
                    ft.Container(
                        bgcolor=self.white,
                        border_radius=8,
                        padding=10,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(pastry_name, size=12, color=self.text_dark),
                                        ft.Text(
                                            format_currency(line_subtotal if line_subtotal is not None else (self._money_to_float(quantity) * self._money_to_float(price))),
                                            size=12,
                                            color=self.text_dark,
                                            weight="w600",
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    f"Qty: {quantity} × {format_currency(price)}",
                                    size=11,
                                    color=self.text_light,
                                ),
                            ],
                        ),
                    )
                )
        else:
            item_controls.append(
                ft.Text(
                    "No items in this order.",
                    size=12,
                    color=self.text_light,
                )
            )

        delivery = order.get("delivery")
        delivery_controls: list[ft.Control]
        if isinstance(delivery, dict):
            delivery_status = delivery.get("status", "")
            delivery_controls = [
                ft.Text(
                    f"Address: {delivery.get('address', 'N/A')}",
                    size=11,
                    color=self.text_light,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Status", size=11, color=self.text_light),
                        ft.Container(
                            bgcolor=get_status_color(delivery_status, "delivery"),
                            border_radius=5,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            content=ft.Text(
                                format_delivery_status(delivery_status),
                                size=11,
                                color=self.white,
                            ),
                        ),
                    ],
                ),
                ft.Text(
                    f"Date: {format_date(delivery.get('date', ''), output_format='%b %d, %Y')}",
                    size=11,
                    color=self.text_light,
                ),
            ]
        else:
            delivery_controls = [
                ft.Text(
                    "No delivery info for this order.",
                    size=11,
                    color=self.text_light,
                )
            ]

        self.detail_panel_body.controls = [
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
                            status_display,
                            size=11,
                            color=self.white,
                        ),
                    ),
                ],
            ),
            ft.Text(
                f"Order date: {format_date(order_date, output_format='%b %d, %Y')}",
                size=11,
                color=self.text_light,
            ),
            ft.Divider(height=1, color=self.light_brown),
            ft.Text("Items", size=12, weight="bold", color=self.text_dark),
            ft.Container(
                height=170,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                    controls=item_controls,
                ),
            ),
            ft.Divider(height=1, color=self.light_brown),
            ft.Text("Totals", size=12, weight="bold", color=self.text_dark),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Subtotal", size=11, color=self.text_light),
                    ft.Text(format_currency(subtotal_value), size=11, color=self.text_light),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Tax", size=11, color=self.text_light),
                    ft.Text(format_currency(tax), size=11, color=self.text_light),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Delivery fee", size=11, color=self.text_light),
                    ft.Text(format_currency(delivery_fee), size=11, color=self.text_light),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Total", size=12, color=self.text_dark, weight="bold"),
                    ft.Text(format_currency(total), size=12, color=self.text_dark, weight="bold"),
                ],
            ),
            ft.Divider(height=1, color=self.light_brown),
            ft.Text("Delivery", size=12, weight="bold", color=self.text_dark),
            *delivery_controls,
        ]

        self._safe_update(self.detail_panel_body)
    
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
                        padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                        content=ft.Text(
                            "Orders",
                            size=24,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Details About Order (inline)
                    ft.Container(
                        padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        content=ft.Container(
                            bgcolor=self.lighter_brown,
                            border_radius=10,
                            padding=15,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        "Details About Order",
                                        size=14,
                                        weight="bold",
                                        color=self.text_dark,
                                    ),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(expand=True, content=self.order_id_field),
                                            self.order_id_load_btn,
                                        ],
                                    ),
                                    ft.Container(
                                        alignment=ft.Alignment.CENTER,
                                        content=self.detail_loading,
                                    ),
                                    self.detail_panel_body,
                                ],
                            ),
                        ),
                    ),
                    
                    ft.Container(height=10),
                    
                    # Filter buttons
                    ft.Container(
                        padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        content=self.filter_buttons,
                    ),
                    
                    ft.Container(height=15),
                    
                    # Loading indicator
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=self.loading,
                    ),
                    
                    # Orders - Receipts
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=15, right=15, top=0, bottom=0),
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
