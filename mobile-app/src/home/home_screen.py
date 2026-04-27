"""
Home screen for the NomNom mobile app.
Displays business stats, top reviews, and user greeting.
"""

import flet as ft
from home.home_service import HomeService
from common.error_handler import get_user_friendly_message, NetworkError


class HomeScreen:
    """Home screen with stats cards and reviews carousel."""
    
    def __init__(self, home_service: HomeService, show_notification):
        """
        Initialize home screen.
        
        Args:
            home_service: HomeService instance
            show_notification: Function to show notifications
        """
        self.home_service = home_service
        self.show_notification = show_notification
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.cream_bg = "#FFF8E1"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.star_yellow = "#FFC107"
        self.white = "#ffffff"
        
        # Data
        self.stats = {}
        self.reviews = []
        self.current_review_index = 0
        
        # Loading state
        self.loading = ft.ProgressRing(color=self.primary_brown)
        
        # Content containers
        self.stats_column = ft.Column(visible=False)
        self.reviews_column = ft.Column(visible=False)
        self.user_greeting = ft.Text(visible=False)
    
    def _create_stat_card(self, title: str, value: str, subtitle: str = "") -> ft.Container:
        """Create a stat card widget."""
        return ft.Container(
            bgcolor=self.lighter_brown,
            border_radius=10,
            padding=15,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(
                        title,
                        size=12,
                        color=self.text_light,
                        weight="w500",
                    ),
                    ft.Text(
                        value,
                        size=28,
                        weight="bold",
                        color=self.text_dark,
                    ),
                    ft.Text(
                        subtitle,
                        size=10,
                        color=self.text_light,
                    ) if subtitle else ft.Container(),
                ],
            ),
        )
    
    def _create_review_card(self, review: dict) -> ft.Container:
        """Create a review card widget."""
        comment = review.get("comment", "No comment")
        user_name = review.get("user_name", "Anonymous")
        
        return ft.Container(
            bgcolor=self.white,
            border=ft.border.all(1, self.light_brown),
            border_radius=10,
            padding=15,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.STAR,
                                color=self.star_yellow,
                                size=16,
                            ),
                            ft.Text(
                                "5 stars",
                                size=12,
                                color=self.text_light,
                            ),
                        ],
                    ),
                    ft.Text(
                        comment,
                        size=13,
                        color=self.text_dark,
                        max_lines=4,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"— {user_name}",
                        size=11,
                        color=self.text_light,
                        italic=True,
                    ),
                ],
            ),
        )
    
    def _load_data(self):
        """Load home screen data from service."""
        try:
            self.stats = self.home_service.get_business_stats()
            self.reviews = self.home_service.get_top_reviews()
            self._update_ui()
        except NetworkError as e:
            self.show_notification(get_user_friendly_message(e), error=True)
    
    def _update_ui(self):
        """Update UI with loaded data."""
        # User greeting (business-wide stats, no specific user name)
        self.user_greeting.value = "Welcome to NomNom!"
        self.user_greeting.visible = True
        
        # Build stats cards - display business-wide statistics
        stats_cards = [
            ft.Row(
                spacing=10,
                controls=[
                    self._create_stat_card(
                        "Total Clients",
                        str(self.stats.get("total_clients", 0)),
                    ),
                    self._create_stat_card(
                        "Total Purchases",
                        str(self.stats.get("total_purchases", 0)),
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self._create_stat_card(
                        "Satisfied Clients",
                        str(self.stats.get("total_satisfied_clients", 0)),
                    ),
                    self._create_stat_card(
                        "Successful Deliveries",
                        str(self.stats.get("total_successful_deliveries", 0)),
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self._create_stat_card(
                        "App Downloads",
                        str(self.stats.get("total_downloads", 0)),
                    ),
                    self._create_stat_card(
                        "",
                        "",
                    ),
                ],
            ),
        ]
        
        self.stats_column.controls = stats_cards
        self.stats_column.visible = True
        
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
    
    def build(self) -> ft.Container:
        """Build and return home screen UI."""
        self._load_data()
        
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(height=20),  # Top padding
                    
                    # User greeting
                    ft.Container(
                        padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                        content=self.user_greeting,
                    ),
                    
                    ft.Container(height=15),
                    
                    # Loading indicator
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=self.loading,
                    ),
                    
                    # Stats section
                    ft.Container(
                        padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        content=self.stats_column,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Reviews section header
                    ft.Container(
                        padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                        content=ft.Text(
                            "Top Reviews",
                            size=18,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    ft.Container(height=10),
                    
                    # Reviews carousel
                    ft.Container(
                        padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        content=self.reviews_column,
                    ),
                    
                    ft.Container(height=40),  # Bottom padding
                ],
                spacing=0,
            ),
        )
