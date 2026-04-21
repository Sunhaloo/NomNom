"""
Map screen for displaying delivery locations.
Displays an interactive map using Flet Map library.
"""

import flet as ft
import flet_map as ftm


class MapScreen:
    """Map screen with location display for deliveries."""
    
    def __init__(self, on_back=None):
        """
        Initialize map screen.
        
        Args:
            on_back: Callback function when back button is clicked
        """
        self.on_back = on_back
        
        # Color scheme
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        
        # Default location (Mauritius center)
        self.initial_latitude = -20.29
        self.initial_longitude = 57.5
        self.initial_zoom = 12
    
    def _on_back_click(self, e):
        """Handle back button click."""
        if self.on_back:
            self.on_back()
    
    def build(self) -> ft.Container:
        """Build and return map screen UI."""
        url_launcher = ft.UrlLauncher()
        
        async def launch_default(url):
            await url_launcher.launch_url(url)
        
        return ftm.Map(
            expand=True,
            initial_center=ftm.MapLatitudeLongitude(
                self.initial_latitude,
                self.initial_longitude
            ),
            initial_zoom=self.initial_zoom,
            layers=[
                ftm.TileLayer(
                    url_template="https://tile.memomaps.de/tilegen/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print(f"TileLayer Error: {e.data}"),
                ),
                ftm.SimpleAttribution(
                    text="OpenStreetMap contributors",
                    on_click=lambda e: launch_default(
                        "https://www.openstreetmap.org/copyright"
                    )
                )
            ],
        )
