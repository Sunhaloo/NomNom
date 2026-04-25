"""
NomNom Mobile App - Main entry point.
Initializes services, router, and app page.
"""

import flet as ft
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from config import API_BASE_URL
from common.storage import StorageManager
from common.api_client import APIClient
from common.error_handler import get_user_friendly_message
from common.navigation import Router
from auth.auth_service import AuthService
from home.home_service import HomeService
from orders.orders_service import OrdersService
from deliveries.deliveries_service import DeliveriesService


def main(page: ft.Page):
    """
    Main app entry point.
    
    Args:
        page: Flet page instance
    """
    # Page configuration
    page.title = "NomNom"
    page.window.width = 400
    page.window.height = 800
    page.padding = 0
    page.margin = 0
    
    # Color scheme
    primary_brown = "#8D6E63"
    white = "#ffffff"
    
    # Initialize storage and services
    storage = StorageManager()
    api_client = APIClient(storage)
    auth_service = AuthService(api_client, storage)
    home_service = HomeService(api_client, storage)
    orders_service = OrdersService(api_client, storage)
    deliveries_service = DeliveriesService(api_client, storage)
    
    # Initialize router
    router = Router(
        auth_service,
        home_service,
        orders_service,
        deliveries_service,
        storage,
    )
    
    # Store page reference in router for access by screens
    router.page = page
    
    # Notification snackbar
    def show_notification(message: str, error: bool = False):
        """Show snackbar notification."""
        snackbar = ft.SnackBar(
            ft.Text(
                message,
                color=white,
                size=13,
            ),
            bgcolor=primary_brown if not error else "#F44336",
            duration=3000,
        )
        page.snack_bar = snackbar
        snackbar.open = True
        page.update()
    
    # Connect notification method to router
    router.show_notification = show_notification
    
    # Main content container
    main_content = ft.Container(expand=True)
    
    # Bottom navigation bar container
    bottom_nav_container = ft.Container()
    
    def update_view():
        """Update main view and navigation."""
        # Check authentication and update current screen if needed
        # Allow deliveries page without login (not yet implemented by auth team)
        if not auth_service.is_logged_in() and router.current_screen not in ["login", "register", "deliveries"]:
            router.current_screen = "login"
        
        # Update main content
        main_content.content = router.get_current_view()
        
        # Show/hide bottom navigation (not shown on auth screens)
        show_nav = router.current_screen not in ["login", "register", "delivery_confirmation"]
        bottom_nav_container.content = router.build_bottom_nav() if show_nav else None
        
        page.update()
    
    # Initial update
    update_view()
    
    # Handle navigation updates (connected to router)
    # Override router methods to trigger view updates
    original_navigate = router._navigate_to
    
    def navigate_to(screen: str):
        """Navigate to screen and update view."""
        original_navigate(screen)
        update_view()
    
    router._navigate_to = navigate_to
    
    # Page structure
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                # Main content
                main_content,
                
                # Bottom navigation
                bottom_nav_container,
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)
