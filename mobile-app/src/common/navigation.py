"""
Router and navigation management for the NomNom mobile app.
Handles screen transitions, bottom navigation, and auth guards.
"""

import flet as ft
from auth.screens.login_screen import LoginScreen
from auth.screens.register_screen import RegisterScreen
from home.home_screen import HomeScreen
from orders.orders_screen import OrdersScreen
from deliveries.deliveries_screen import DeliveriesScreen
from deliveries.delivery_confirmation_screen import DeliveryConfirmationScreen


class Router:
    """Manages navigation and screen routing."""
    
    def __init__(
        self,
        auth_service,
        home_service,
        orders_service,
        deliveries_service,
        storage,
    ):
        """
        Initialize router.
        
        Args:
            auth_service: AuthService instance
            home_service: HomeService instance
            orders_service: OrdersService instance
            deliveries_service: DeliveriesService instance
            storage: StorageManager instance
        """
        self.auth_service = auth_service
        self.home_service = home_service
        self.orders_service = orders_service
        self.deliveries_service = deliveries_service
        self.storage = storage
        
        # Page reference (set after router initialization in main.py)
        self.page = None
        
        # Screen state
        # Start with login page
        self.current_screen = "login"
        self.current_delivery_id = None
        self.showing_map = False
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.text_dark = "#3E2723"
        self.white = "#ffffff"
    
    def show_notification(self, message: str, error: bool = False):
        """
        Show snackbar notification (to be connected to page).
        
        Args:
            message: Notification message
            error: Whether this is an error notification
        """
        # This will be implemented in main.py with page reference
        pass
    
    def get_current_view(self) -> ft.Container:
        """
        Get current screen view.
        
        Returns:
            Current screen Container
        """
        if self.current_screen == "login":
            return LoginScreen(
                self.auth_service,
                self._on_login_success,
                self.show_notification,
                router=self,
            ).build()
        
        elif self.current_screen == "register":
            return RegisterScreen(
                self.auth_service,
                self._on_signup_success,
                self.show_notification,
                self,
            ).build()
        
        elif self.current_screen == "home":
            return HomeScreen(
                self.home_service,
                self.show_notification,
                router=self,
            ).build()
        
        elif self.current_screen == "orders":
            return OrdersScreen(
                self.orders_service,
                self.show_notification,
            ).build()
        
        elif self.current_screen == "deliveries":
            return DeliveriesScreen(
                self.deliveries_service,
                self.show_notification,
            ).build(page=self.page)
        
        elif self.current_screen == "delivery_confirmation":
            return DeliveryConfirmationScreen(
                self.deliveries_service,
                self.current_delivery_id,
                self._on_delivery_confirmed,
                lambda: self._navigate_to("deliveries"),
                self.show_notification,
            ).build()
        
        return ft.Container(content=ft.Text("Screen not found"))
    
    def _navigate_to(self, screen: str):
        """Navigate to a screen."""
        self.current_screen = screen
    
    def navigate(self, screen: str):
        """Alias for _navigate_to for external calls."""
        self._navigate_to(screen)
    
    def logout(self):
        """Log out current user and navigate to login."""
        try:
            self.auth_service.logout()
            self._navigate_to("login")
        except Exception as e:
            self.show_notification(f"Logout error: {str(e)}", error=True)
            # Still navigate to login to be safe
            self._navigate_to("login")
    
    def _navigate_to_delivery_confirmation(self, delivery_id: int):
        """Navigate to delivery confirmation screen."""
        self.current_delivery_id = delivery_id
        self._navigate_to("delivery_confirmation")
    
    def _on_login_success(self, result):
        """Handle successful login."""
        self._navigate_to("home")
    
    def _on_signup_success(self, result):
        """Handle successful signup."""
        self._navigate_to("home")
    
    def _on_delivery_confirmed(self, result):
        """Handle successful delivery confirmation."""
        self._navigate_to("deliveries")
    
    def build_bottom_nav(self) -> ft.BottomAppBar:
        """Build bottom navigation bar."""
        return ft.BottomAppBar(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.HOME,
                        icon_color=self.primary_brown if self.current_screen == "home" else "#8B7355",
                        opacity=1.0 if self.current_screen == "home" else 0.85,
                        on_click=lambda e: self._navigate_to("home"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SHOPPING_CART,
                        icon_color=self.primary_brown if self.current_screen == "orders" else "#8B7355",
                        opacity=1.0 if self.current_screen == "orders" else 0.85,
                        on_click=lambda e: self._navigate_to("orders"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LOCAL_SHIPPING,
                        icon_color=self.primary_brown if self.current_screen == "deliveries" else "#8B7355",
                        opacity=1.0 if self.current_screen == "deliveries" else 0.85,
                        on_click=lambda e: self._navigate_to("deliveries"),
                    ),
                ],
            ),
        )
    
    def build_main_content(self) -> ft.Container:
        """Build main content area."""
        # Check if user is authenticated
        # Allow deliveries page without login (not yet implemented by auth team)
        if not self.auth_service.is_logged_in() and self.current_screen not in ["login", "register", "deliveries"]:
            self.current_screen = "login"
        
        return ft.Container(
            expand=True,
            content=self.get_current_view(),
        )
