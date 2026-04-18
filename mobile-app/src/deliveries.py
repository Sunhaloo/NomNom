import flet as ft
import http.client
import json


class DeliveriesPage:
    def __init__(self, page: ft.Page, on_back_callback=None):
        self.page = page
        self.on_back_callback = on_back_callback
        self.current_location = {"lat": 40.7128, "lon": -74.0060}
        self.pending_deliveries = []
        self.confirmed_deliveries = []
        self.cancelled_deliveries = []
        self.api_host = "localhost"
        self.api_port = 8000
        self.auth_token = None

    def _make_api_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make HTTP request to Django REST API"""
        try:
            conn = http.client.HTTPConnection(self.api_host, self.api_port)
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            body = json.dumps(data) if data else None
            conn.request(method, f"/api{endpoint}", body, headers)
            response = conn.getresponse()
            response_data = response.read().decode()
            conn.close()
            return json.loads(response_data) if response_data else {}
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_deliveries_from_api(self):
        """Fetch deliveries from API"""
        try:
            response = self._make_api_request("/deliveries/")
            if isinstance(response, list):
                self.pending_deliveries = [d for d in response if d.get("status") == "pending"]
                self.confirmed_deliveries = [d for d in response if d.get("status") == "confirmed"]
                self.cancelled_deliveries = [d for d in response if d.get("status") == "cancelled"]
        except:
            pass
    
    def _get_delivery_card(self, delivery, status_color, status_label) -> ft.Container:
        """Create a delivery card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Delivery #{delivery.get('id', '?')}", weight="bold", size=12),
                    ft.Text(f"📍 {delivery.get('address', 'N/A')}", size=10, color="#616161"),
                    ft.Text(f"{status_label}", size=10, weight="bold", color=status_color),
                ],
                spacing=5,
            ),
            padding=12,
            border_radius=8,
            expand=True,
            margin=ft.margin.symmetric(vertical=5),
        )

    def build(self) -> ft.Column:
        """Build deliveries page - centered, full width"""
        self._fetch_deliveries_from_api()
        
        # ========== MAP SECTION ==========
        map_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.MAP, size=80, color="#1976D2"),
                    ft.Text("🗺️ Interactive Map", size=18, weight="bold", text_align=ft.TextAlign.CENTER),
                    ft.Text("Current Location: NYC", size=12, color="#616161", text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Lat: {self.current_location['lat']:.4f}", size=11, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Lon: {self.current_location['lon']:.4f}", size=11, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            height=250,
            expand=False,
            width=500,
            bgcolor="#F5F5F5",
            border=ft.border.all(2, "#1976D2"),
            border_radius=10,
            padding=20,
        )

        # ========== PENDING DELIVERIES ==========
        pending_controls = []
        if self.pending_deliveries:
            for delivery in self.pending_deliveries:
                card = self._get_delivery_card(delivery, "#F57F17", "⏳ PENDING")
                card.bgcolor = "#FFF8E1"
                card.border = ft.border.all(2, "#FFB300")
                pending_controls.append(card)
        else:
            pending_controls.append(ft.Text("No pending deliveries", color="#999999", size=11))

        pending_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("⏳ PENDING DELIVERIES", size=13, weight="bold", color="#F57F17"),
                    ft.Column(controls=pending_controls, scroll=ft.ScrollMode.AUTO, height=140, expand=True),
                ],
                spacing=10,
            ),
            expand=True,
            width=500,
            border_radius=10,
            padding=12,
            bgcolor="#FFFBF0",
            border=ft.border.all(1, "#FFE082"),
        )

        # ========== CONFIRMED DELIVERIES ==========
        confirmed_controls = []
        if self.confirmed_deliveries:
            for delivery in self.confirmed_deliveries:
                card = self._get_delivery_card(delivery, "#388E3C", "✅ CONFIRMED")
                card.bgcolor = "#E8F5E9"
                card.border = ft.border.all(2, "#4CAF50")
                confirmed_controls.append(card)
        else:
            confirmed_controls.append(ft.Text("No confirmed deliveries", color="#999999", size=11))

        confirmed_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("✅ CONFIRMED DELIVERIES", size=13, weight="bold", color="#388E3C"),
                    ft.Column(controls=confirmed_controls, scroll=ft.ScrollMode.AUTO, height=140, expand=True),
                ],
                spacing=10,
            ),
            expand=True,
            width=500,
            border_radius=10,
            padding=12,
            bgcolor="#F1F8F4",
            border=ft.border.all(1, "#81C784"),
        )

        # ========== CANCELLED DELIVERIES ==========
        cancelled_controls = []
        if self.cancelled_deliveries:
            for delivery in self.cancelled_deliveries:
                card = self._get_delivery_card(delivery, "#C62828", "❌ CANCELLED")
                card.bgcolor = "#FFEBEE"
                card.border = ft.border.all(2, "#F44336")
                cancelled_controls.append(card)
        else:
            cancelled_controls.append(ft.Text("No cancelled deliveries", color="#999999", size=11))

        cancelled_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("❌ CANCELLED DELIVERIES", size=13, weight="bold", color="#C62828"),
                    ft.Column(controls=cancelled_controls, scroll=ft.ScrollMode.AUTO, height=140, expand=True),
                ],
                spacing=10,
            ),
            expand=True,
            width=500,
            border_radius=10,
            padding=12,
            bgcolor="#FEF5F5",
            border=ft.border.all(1, "#EF9A9A"),
        )

        # ========== MAIN PAGE CONTENT ==========
        content = ft.Column(
            controls=[
                ft.AppBar(
                    title=ft.Text("🚚 Deliveries & Map", weight="bold"),
                    bgcolor="#1976D2",
                    actions=[
                        ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: self._on_refresh_location_click(e)),
                    ],
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            map_section,
                            ft.Divider(height=20),
                            pending_section,
                            confirmed_section,
                            cancelled_section,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    padding=15,
                ),
            ],
            expand=True,
            spacing=0,
        )

        return content

    def _on_refresh_location_click(self, e):
        """Refresh location and deliveries"""
        self._fetch_deliveries_from_api()
        self.page.update()

    def _on_go_back(self, e):
        """Go back to home page"""
        if self.on_back_callback:
            self.on_back_callback()
