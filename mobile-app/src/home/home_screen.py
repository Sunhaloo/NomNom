"""
Home screen for the NomNom mobile app.
Displays business stats, top reviews, and user greeting.
"""

import flet as ft
import threading
import time
from home.home_service import HomeService
from common.error_handler import get_user_friendly_message, NetworkError
from config import SERVER_BASE_URL


class HomeScreen:
    """Home screen with stats cards and reviews carousel."""
    
    def __init__(self, home_service: HomeService, show_notification, router: any = None):
        """
        Initialize home screen.
        
        Args:
            home_service: HomeService instance
            show_notification: Function to show notifications
        """
        self.home_service = home_service
        self.router = router
        self.show_notification = show_notification
        
        # Color scheme
        self.primary_brown = "#8B5E3C"
        self.light_brown = "#E6D3C5"
        self.lighter_brown = "#F3E5DC"
        self.cream_bg = "#FAF3EE"
        self.text_dark = "#3B2F2F"
        self.text_light = "#7A5C58"
        self.white = "#ffffff"
        self.black = "#000000"
        self.pale_grey = "#f5f5f5"
        self.content_width = 380

        self.card_shadow = ft.BoxShadow(
            blur_radius=14,
            spread_radius=0,
            offset=ft.Offset(0, 3),
            color="#00000026",
        )
        
        # Data
        self.stats = {}
        self.reviews = []
        self.current_review_index = 0
        self.pastries = []
        self.current_pastry_index = 0
        self.banner_stop_flag = False
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown)
        
        # Content containers
        self.stats_column = ft.Column(visible=False, spacing=15)
        self.reviews_column = ft.Column(visible=False)
        self.user_greeting = ft.Text(size=22, weight="bold", color=self.text_dark, visible=False)
        # Container for displaying user profile data in a card
        self.user_profile_card = ft.Container(
            visible=False,
            bgcolor=self.white,
            border_radius=15,
            padding=18,
            shadow=self.card_shadow,
            content=ft.Column(spacing=6, controls=[]),
        )
        
        # Banner carousel container
        self.banner_container = ft.Container(
            visible=False,
            bgcolor=self.lighter_brown,
            border_radius=15,
            padding=15,
            shadow=self.card_shadow,
            height=250,
            width=self.content_width,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[],
            ),
        )

    
    def _create_stat_card(self, title: str, value: str, icon: str):
        """Create a stat card widget."""
        return ft.Container(
            expand=True,
            bgcolor=self.lighter_brown,
            border_radius=18,
            padding=15,
            shadow=self.card_shadow,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row([
                        ft.Icon(icon, color=self.primary_brown, size=20),
                        ft.Text(title, size=13, color=self.text_light),
                    ]),
                    ft.Text(value, size=28, weight="bold", color=self.text_dark),
                ],
            ),
        )
    
    def _load_data(self):
        """Load home screen data from service."""
        self.loading.visible = True
        try:
            if self.loading.page:
                self.loading.update()
        except Exception:
            pass
        
        try:
            self.stats = self.home_service.get_business_stats()
            self.reviews = self.home_service.get_top_reviews()
            # Fetch user profile data from backend
            self.user_profile = self.home_service.get_user_profile()
            # Fetch pastries for banner
            self.pastries = self.home_service.get_pastries_banner()
            self._update_ui()
            # Start banner rotation in background thread
            if self.pastries:
                self.banner_stop_flag = False
                threading.Thread(target=self._rotate_banner, daemon=True).start()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.loading.visible = False
            try:
                if self.loading.page:
                    self.loading.update()
            except Exception:
                pass
    
    def _safe_update(self, control: ft.Control):
        """Safely update a control if it's attached to a page."""
        try:
            if hasattr(control, 'page') and control.page:
                control.update()
        except Exception:
            pass

    def _wrap(self, control: ft.Control) -> ft.Control:
        """Keep content centered with a consistent max width."""
        return ft.Container(
            width=self.content_width,
            alignment=ft.Alignment.TOP_CENTER,
            content=control,
        )

    def _resolve_image_src(self, image_src: str) -> str:
        """Resolve relative media paths into absolute URLs for Flet Image."""
        if not image_src:
            return ""
        if image_src.startswith("http://") or image_src.startswith("https://"):
            return image_src
        if image_src.startswith("/"):
            return f"{SERVER_BASE_URL}{image_src}"
        return f"{SERVER_BASE_URL}/{image_src}"
    
    def _update_ui(self):
        """Update UI with loaded data."""
        profile = getattr(self, 'user_profile', {})
        first_name = (profile.get("first_name") or "").strip()
        last_name = (profile.get("last_name") or "").strip()
        display_name = " ".join(part for part in [first_name, last_name] if part) or "Customer"

        # Avoid repeating "NomNom" since the header already shows the brand.
        self.user_greeting.value = f"Welcome,\n{display_name}!"
        self.user_greeting.visible = True
        # Populate user profile card with data
        
        self.user_profile_card.content = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.PERSON, color=self.primary_brown, size=18),
                                ft.Text("Customer Info", weight="bold", size=16, color=self.text_dark),
                            ],
                        ),
                        ft.Icon(ft.Icons.BADGE, color=self.primary_brown, size=18),
                    ],
                ),
                ft.Divider(height=1, color=self.light_brown),
                ft.Text("Name:", color=self.text_light, weight="bold"),
                ft.Text(first_name or "—", color=self.text_light),
                ft.Text(last_name or "—", color=self.text_light),
                ft.Text(f"Address: {profile.get('street', '')}", color=self.text_light),
                ft.Text(f"Region: {profile.get('region', '')}", color=self.text_light),
            ],
        )
        self.user_profile_card.visible = True
        
                 # Build stats cards 
        self.stats_column.controls = [
            ft.Row([
                self._create_stat_card("Total Clients", str(self.stats.get("total_clients", 0)), ft.Icons.PEOPLE_ALT_SHARP),
                self._create_stat_card("Number of Orders", str(self.stats.get("total_purchases", 0)), ft.Icons.SHOPPING_CART),
            ]),
            ft.Row([
                self._create_stat_card("Satisfied Clients", str(self.stats.get("total_satisfied_clients", 0)), ft.Icons.TAG_FACES_ROUNDED),
                self._create_stat_card("Successful Deliveries", str(self.stats.get("total_successful_deliveries", 0)), ft.Icons.LOCAL_SHIPPING),
            ]),
            ft.Row([
                self._create_stat_card("App Downloads", str(self.stats.get("total_downloads", 0)), ft.Icons.DOWNLOAD),
                self._create_stat_card("Top Reviews", str(self.stats.get("top_reviews", 0)), ft.Icons.STAR),
            ]),
        ]
        self.stats_column.visible = True
        
        # Build banner carousel
        if self.pastries and len(self.pastries) > 0:
            self._update_banner_display()
            self.banner_container.visible = True
        
        # Build review carousel
        if self.reviews and len(self.reviews) > 0:
            self.reviews_column.controls = [
                self._create_review_card(self.reviews[0]),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=self._prev_review,
                            icon_color=self.primary_brown,
                        ),
                        ft.Text(
                            f"{self.current_review_index + 1}/{len(self.reviews)}",
                            size=12,
                            color=self.text_light,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=self._next_review,
                            icon_color=self.primary_brown,
                        ),
                    ],
                ),
            ]
            self.reviews_column.visible = True
        else:
            # No reviews available, show empty state
            self.reviews_column.controls = [
                ft.Text(
                    "No reviews available yet",
                    size=14,
                    color=self.text_light,
                    text_align=ft.TextAlign.CENTER,
                ),
            ]
            self.reviews_column.visible = True
    
    def _create_review_card(self, review: dict):
        """Create a review card widget."""
        return ft.Container(
            bgcolor=self.white,
            border_radius=15,
            padding=20,
            shadow=self.card_shadow,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(review.get("user_name", "Anonymous"), weight="bold", color=self.text_dark),
                            ft.Row([
                                ft.Icon(ft.Icons.STAR, color=self.primary_brown, size=16),
                                ft.Text(str(review.get("rating", 5)), size=14, weight="bold", color=self.text_dark),
                            ]),
                        ],
                    ),
                    ft.Text(
                        review.get("comment", ""),
                        size=14,
                        color=self.text_light,
                        italic=True,
                    ),
                    ft.Text(
                        review.get("date", ""),
                        size=12,
                        color=self.text_light,
                        italic=False,
                    ),
                ],
            ),
        )
    
    def _prev_review(self, e):
        """Show previous review."""
        if self.current_review_index > 0:
            self.current_review_index -= 1
            self._update_review_carousel()
    
    def _next_review(self, e):
        """Show next review."""
        if self.current_review_index < len(self.reviews) - 1:
            self.current_review_index += 1
            self._update_review_carousel()
    
    def _update_review_carousel(self):
        """Update review carousel display."""
        review_card = self._create_review_card(self.reviews[self.current_review_index])
        counter = ft.Text(
            f"{self.current_review_index + 1}/{len(self.reviews)}",
            size=12,
            color=self.text_light,
        )
        
        self.reviews_column.controls[0] = review_card
        self.reviews_column.controls[1].controls[1] = counter
        self.reviews_column.update()
    
    def _create_banner_card(self, pastry: dict):
        """Create a pastry card for the banner carousel."""
        image_src = self._resolve_image_src(pastry.get("image", "") or "")
        
        image_widget = ft.Image(
            src=image_src,
            width=180,
            height=150,
            fit=ft.BoxFit.COVER,
            error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=60, color=self.text_light),
        ) if image_src else ft.Icon(ft.Icons.CAKE, size=60, color=self.primary_brown)
        
        return ft.Container(
            bgcolor=self.white,
            border_radius=12,
            padding=12,
            shadow=self.card_shadow,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    image_widget,
                    ft.Container(height=8),
                    ft.Text(
                        pastry.get("name", "Unknown"),
                        size=14,
                        weight="bold",
                        color=self.text_dark,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"${pastry.get('price', '0')}",
                        size=12,
                        color=self.primary_brown,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        pastry.get("category", ""),
                        size=11,
                        color=self.text_light,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=6,
            ),
        )
    
    def _rotate_banner(self):
        """Background thread to rotate banner every 30 seconds."""
        while not self.banner_stop_flag and self.pastries:
            try:
                time.sleep(30)
                if not self.banner_stop_flag:
                    self.current_pastry_index = (self.current_pastry_index + 1) % len(self.pastries)
                    self._update_banner_display()
            except Exception as e:
                print(f"Banner rotation error: {e}")
    
    def _update_banner_display(self):
        """Update banner to show current pastry."""
        try:
            if self.pastries and len(self.pastries) > 0:
                pastry_card = self._create_banner_card(self.pastries[self.current_pastry_index])
                indicator = ft.Text(
                    f"{self.current_pastry_index + 1}/{len(self.pastries)}",
                    size=11,
                    color=self.text_light,
                )
                
                self.banner_container.content.controls = [
                    pastry_card,
                    ft.Container(height=8),
                    indicator,
                ]
                self._safe_update(self.banner_container)
        except Exception as e:
            print(f"Banner display error: {e}")
    
    def build(self) -> ft.Container:
        """Build and return home screen UI."""
        self._load_data()
        
        return ft.Container(
            expand=True,
            bgcolor=self.cream_bg,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self._wrap(
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Image(
                                    src="NomNom-Logo-mark.png",
                                    width=70,
                                    height=70,
                                    fit=ft.BoxFit.CONTAIN,
                                ),
                                ft.Container(width=10),
                                ft.Text("NomNom", size=22, weight="bold", color=self.black),
                            ],
                        )
                    ),

                    ft.Container(height=10),

                    self._wrap(
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=self.loading,
                        )
                    ),

                    self._wrap(self.user_greeting),
                    ft.Container(height=12),

                    self._wrap(self.user_profile_card),
                    ft.Container(height=18),
                    
                    self._wrap(ft.Text("Featured Pastries", size=18, weight="bold", color=self.black)),
                    ft.Container(height=10),
                    self.banner_container,
                    ft.Container(height=20),

                    self._wrap(ft.Text("Overview", size=18, weight="bold", color=self.black)),
                    ft.Container(height=10),
                    self._wrap(self.stats_column),
                    ft.Container(height=22),

                    self._wrap(ft.Text("Top Reviews", size=18, weight="bold", color=self.black)),
                    ft.Container(height=10),
                    self._wrap(self.reviews_column),
                    ft.Container(height=22),

                    self._wrap(
                        ft.FilledButton(
                            content=ft.Text("Logout"),
                            bgcolor=self.primary_brown,
                            color=self.white,
                            height=48,
                            on_click=lambda e: self.router.logout() if self.router else None,
                        )
                    ),
                    ft.Container(height=10),
                ],
            ),
        )
