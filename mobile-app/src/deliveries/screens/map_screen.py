"""
Delivery map screen with live location tracking
"""

import flet as ft
import flet_map as ftm
import flet_geolocator as ftg


class MapScreen:
    """Shows an interactive map with your current location"""
    
    def __init__(self, on_back=None):
        """Set up the map"""
        self.on_back = on_back
        
        # Colors
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        
        # Start centered on Mauritius
        self.initial_latitude = -20.29
        self.initial_longitude = 57.5
        self.initial_zoom = 12
        
        self.current_latitude = self.initial_latitude
        self.current_longitude = self.initial_longitude
        
        self.geo = None
        self.page = None
        self.map_instance = None
    
    def _handle_position_change(self, e: ftg.GeolocatorPositionChangeEvent):
        """When location updates, move map to follow"""
        if e.position:
            self.current_latitude = e.position.latitude
            self.current_longitude = e.position.longitude
            if self.map_instance:
                self.map_instance.center = ftm.MapLatitudeLongitude(
                    self.current_latitude,
                    self.current_longitude
                )
    
    def _handle_error(self, e):
        """Show location error to user"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Location Error: {e.data}", color=self.white),
                bgcolor="#F44336",
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    async def _handle_get_current_position(self, e):
        """Fetch and show current GPS location"""
        if self.geo and self.page:
            try:
                print("[GEOLOCATION] Requesting current position...")
                p = await self.geo.get_current_position()
                print(f"[GEOLOCATION] Position received: {p}")
                if p:
                    print(f"[GEOLOCATION] Lat: {p.latitude}, Lon: {p.longitude}")
                    self.current_latitude = p.latitude
                    self.current_longitude = p.longitude
                    if self.map_instance:
                        print(f"[GEOLOCATION] Updating map center...")
                        self.map_instance.center = ftm.MapLatitudeLongitude(
                            self.current_latitude,
                            self.current_longitude
                        )
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Location: ({p.latitude:.4f}, {p.longitude:.4f})", color=self.white),
                        bgcolor=self.primary_brown,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    print("[GEOLOCATION] Success!")
                else:
                    print("[GEOLOCATION] No position returned")
            except Exception as ex:
                print(f"[GEOLOCATION] Error: {str(ex)}")
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error getting location: {str(ex)}", color=self.white),
                        bgcolor="#F44336",
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
    
    def build(self, page: ft.Page = None) -> ft.Container:
        """Create the map view"""
        self.page = page
        url_launcher = ft.UrlLauncher()
        
        async def launch_default(url):
            await url_launcher.launch_url(url)
        
        # Set up location tracking
        if self.page:
            self.geo = ftg.Geolocator(
                configuration=ftg.GeolocatorConfiguration(
                    accuracy=ftg.GeolocatorPositionAccuracy.LOW
                ),
                on_position_change=self._handle_position_change,
                on_error=self._handle_error,
            )
        
        # Create the map
        self.map_instance = ftm.Map(
            expand=True,
            initial_center=ftm.MapLatitudeLongitude(
                self.initial_latitude,
                self.initial_longitude
            ),
            initial_zoom=self.initial_zoom,
            layers=[
                ftm.TileLayer(
                    url_template="https://tile.memomaps.de/tilegen/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print(f"Tile load error: {e.data}"),
                ),
                ftm.SimpleAttribution(
                    text="OpenStreetMap contributors",
                    on_click=lambda e: launch_default(
                        "https://www.openstreetmap.org/copyright"
                    )
                )
            ],
        )
        
        # Button to find your location
        my_location_btn = ft.FilledButton(
            content=ft.Text("📍 My Location", size=12),
            bgcolor=self.primary_brown,
            color=self.white,
            on_click=self._handle_get_current_position,
        )
        
        # Main layout with map and controls
        return ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=8,
                controls=[
                    # Title
                    ft.Text(
                        "Delivery Map",
                        size=16,
                        weight="bold",
                        color=self.text_dark,
                    ),
                    # Show delivery map
                    ft.Container(
                        expand=True,
                        content=self.map_instance,
                    ),
                    # Find my location button
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[my_location_btn],
                    ),
                ],
            ),
        )
