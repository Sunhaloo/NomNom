"""
Delivery map screen with live location tracking
"""

import asyncio
import math

import flet as ft
import flet_map as ftm
import flet_geolocator as ftg
import requests

from config import OSRM_BASE_URL, OSRM_PROFILE, SHOP_LATITUDE, SHOP_LONGITUDE


class MapScreen:
    """Shows an interactive map with shop + customer location and a simple path."""
    
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
        
        # Customer (device) location - unknown until retrieved
        self.customer_latitude = None
        self.customer_longitude = None
        
        self.geo = None
        self.page = None
        self.map_instance = None
        self.customer_marker = None
        self.marker_layer = None
        self.route_polyline = None
        self.route_layer = None
        self._route_cache = {}
        self._route_fetch_in_flight = False

    def request_customer_location(self) -> None:
        """Fetch the customer's (device) GPS location and update the map."""
        if self.geo and self.page:
            self.page.run_task(self._get_current_position_async)
    
    def _handle_position_change(self, e: ftg.GeolocatorPositionChangeEvent):
        """When location updates, refresh customer marker + route."""
        if e.position:
            self._set_customer_location(
                latitude=e.position.latitude,
                longitude=e.position.longitude,
                move_map=False,
                show_snackbar=False,
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

    def _safe_update(self, control: ft.Control) -> None:
        """Update a control if it is attached to the page."""
        try:
            control.update()
        except RuntimeError:
            pass

    def _calculate_distance_km(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Haversine distance (km) between two coordinates."""
        earth_radius_km = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return earth_radius_km * c

    async def _move_map_async(
        self,
        *,
        destination: ftm.MapLatitudeLongitude,
        zoom: float | None = None,
    ) -> None:
        """Move map camera; supports both sync and async `move_to()` implementations."""
        if not self.map_instance:
            return

        result = self.map_instance.move_to(
            destination=destination,
            zoom=zoom,
            cancel_ongoing_animations=True,
        )
        if asyncio.iscoroutine(result):
            await result
        self._safe_update(self.map_instance)

    def _route_cache_key(self, dest_latitude: float, dest_longitude: float) -> str:
        """Cache key for a route (rounded to reduce churn)."""
        return f"{SHOP_LATITUDE:.5f},{SHOP_LONGITUDE:.5f}->{dest_latitude:.5f},{dest_longitude:.5f}"

    def _fetch_osrm_route_geojson(
        self,
        dest_latitude: float,
        dest_longitude: float,
    ) -> tuple[list[ftm.MapLatitudeLongitude] | None, float | None]:
        """
        Fetch a road route from OSRM and return (route_points, distance_km).

        Uses OSRM `geometries=geojson`, so we get an ordered list of [lon, lat].
        """
        url = (
            f"{OSRM_BASE_URL.rstrip('/')}/route/v1/{OSRM_PROFILE}/"
            f"{SHOP_LONGITUDE},{SHOP_LATITUDE};{dest_longitude},{dest_latitude}"
        )
        params = {
            "overview": "full",
            "geometries": "geojson",
            "alternatives": "false",
            "steps": "false",
        }

        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        payload = response.json()

        routes = payload.get("routes") if isinstance(payload, dict) else None
        if not routes:
            return None, None

        route0 = routes[0]
        geometry = route0.get("geometry", {})
        coords = geometry.get("coordinates") if isinstance(geometry, dict) else None
        if not isinstance(coords, list) or len(coords) < 2:
            return None, None

        points = []
        for item in coords:
            if (
                isinstance(item, list)
                and len(item) >= 2
                and isinstance(item[0], (int, float))
                and isinstance(item[1], (int, float))
            ):
                lon, lat = item[0], item[1]
                points.append(ftm.MapLatitudeLongitude(lat, lon))

        distance_m = route0.get("distance")
        distance_km = (float(distance_m) / 1000.0) if isinstance(distance_m, (int, float)) else None

        return (points if len(points) >= 2 else None), distance_km

    async def _update_route_async(self, dest_latitude: float, dest_longitude: float) -> None:
        """Update the displayed polyline to follow roads (fallback: straight line)."""
        if not self.page or not self.route_polyline or not self.route_layer:
            return
        if self._route_fetch_in_flight:
            return

        cache_key = self._route_cache_key(dest_latitude, dest_longitude)
        cached = self._route_cache.get(cache_key)
        if cached:
            points, distance_km = cached
        else:
            self._route_fetch_in_flight = True
            try:
                points, distance_km = await asyncio.to_thread(
                    self._fetch_osrm_route_geojson,
                    dest_latitude,
                    dest_longitude,
                )
                if points:
                    self._route_cache[cache_key] = (points, distance_km)
            except Exception as ex:
                print(f"[ROUTING] OSRM route fetch failed: {ex}")
                return
            finally:
                self._route_fetch_in_flight = False

        if not points:
            return

        # Replace straight line with road-following geometry.
        self.route_polyline.coordinates = points
        self._safe_update(self.route_polyline)

        # Recenter to the midpoint and zoom for the route distance.
        if isinstance(distance_km, (int, float)):
            zoom = self._zoom_for_route_distance(float(distance_km))
            # Midpoint heuristic still works reasonably for small routes.
            mid_index = len(points) // 2
            mid = points[mid_index]
            await self._move_map_async(destination=mid, zoom=zoom)

    def _zoom_for_route_distance(self, distance_km: float) -> float:
        """Heuristic zoom so both ends of the route are likely visible."""
        # Note: larger zoom value => more zoomed in. We bias toward zooming out so
        # both endpoints of the polyline are visible on smaller map viewports.
        if distance_km < 0.5:
            return 15
        if distance_km < 2:
            return 14
        if distance_km < 6:
            return 13
        if distance_km < 15:
            return 12
        if distance_km < 35:
            return 11
        return 10

    def _set_customer_location(
        self,
        *,
        latitude: float,
        longitude: float,
        move_map: bool = True,
        show_snackbar: bool = True,
    ) -> None:
        """Set customer (device) GPS location, update marker + route, optionally recenter map."""
        self.customer_latitude = latitude
        self.customer_longitude = longitude

        if self.customer_marker:
            self.customer_marker.visible = True
            self.customer_marker.coordinates = ftm.MapLatitudeLongitude(latitude, longitude)
            self._safe_update(self.customer_marker)
        if self.marker_layer:
            self._safe_update(self.marker_layer)

        if self.route_polyline:
            self.route_polyline.coordinates = [
                ftm.MapLatitudeLongitude(SHOP_LATITUDE, SHOP_LONGITUDE),
                ftm.MapLatitudeLongitude(latitude, longitude),
            ]
            self._safe_update(self.route_polyline)

        if self.route_layer:
            self.route_layer.visible = True
            self._safe_update(self.route_layer)

        if self.map_instance and move_map:
            distance_km = self._calculate_distance_km(
                SHOP_LATITUDE,
                SHOP_LONGITUDE,
                latitude,
                longitude,
            )
            zoom = self._zoom_for_route_distance(distance_km)
            mid_latitude = (SHOP_LATITUDE + latitude) / 2
            mid_longitude = (SHOP_LONGITUDE + longitude) / 2
            self.page.run_task(
                self._move_map_async,
                destination=ftm.MapLatitudeLongitude(mid_latitude, mid_longitude),
                zoom=zoom,
            )
            self.page.run_task(self._update_route_async, latitude, longitude)

        if self.page and show_snackbar:
            try:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(
                        f"Customer location: ({latitude:.4f}, {longitude:.4f})",
                        color=self.white,
                    ),
                    bgcolor=self.primary_brown,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except RuntimeError:
                pass
    
    def _on_location_click(self, e):
        """Non-async wrapper for getting current position."""
        # This will be called from on_click, which doesn't support async
        # The actual async work will be handled by the page's async context
        if self.geo and self.page:
            print("[GEOLOCATION] Location button clicked")
            # Schedule the async operation on the page's event loop
            self.page.run_task(self._get_current_position_async)
    
    async def _get_current_position_async(self):
        """Async method to fetch and show customer (device) GPS location."""
        if self.geo and self.page:
            try:
                print("[GEOLOCATION] Requesting current position...")
                p = await self.geo.get_current_position()
                print(f"[GEOLOCATION] Position received: {p}")
                if p:
                    print(f"[GEOLOCATION] Lat: {p.latitude}, Lon: {p.longitude}")
                    self._set_customer_location(
                        latitude=p.latitude,
                        longitude=p.longitude,
                        move_map=True,
                        show_snackbar=True,
                    )
                    print("[GEOLOCATION] Success!")
                else:
                    print("[GEOLOCATION] No position returned")
            except PermissionError:
                print("[GEOLOCATION] Permission denied to access location")
                if self.page:
                    try:
                        self.page.snack_bar = ft.SnackBar(
                            ft.Text(
                                "Location permission denied. Please enable in settings.",
                                color=self.white,
                            ),
                            bgcolor="#F44336",
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except RuntimeError:
                        pass
            except Exception as ex:
                print(f"[GEOLOCATION] Error: {str(ex)}")
                if self.page:
                    try:
                        self.page.snack_bar = ft.SnackBar(
                            ft.Text(f"Error getting location: {str(ex)}", color=self.white),
                            bgcolor="#F44336",
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except RuntimeError:
                        pass
    
    def _handle_tile_error(self, e):
        """Handle tile loading errors with user notification"""
        print(f"Tile load error: {e.data}")
        if self.page:
            try:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(
                        "Map tiles unavailable. Using fallback server.",
                        color=self.white,
                        size=12,
                    ),
                    bgcolor="#FF9800",
                    duration=2000,
                )
                self.page.snack_bar.open = True
                self.page.update()
            except RuntimeError:
                # SnackBar might not be added to page yet
                pass
    
    def build(self, page: ft.Page = None) -> ft.Container:
        """Create the map view"""
        self.page = page

        def on_attribution_click(e):
            if self.page:
                self.page.launch_url("https://www.openstreetmap.org/copyright")
        
        # Set up location tracking
        if self.page:
            self.geo = ftg.Geolocator(
                configuration=ftg.GeolocatorConfiguration(
                    accuracy=ftg.GeolocatorPositionAccuracy.LOW
                ),
                on_position_change=self._handle_position_change,
                on_error=self._handle_error,
            )

        shop_marker = ftm.Marker(
            coordinates=ftm.MapLatitudeLongitude(SHOP_LATITUDE, SHOP_LONGITUDE),
            content=ft.Container(
                content=ft.Icon(ft.Icons.STORE, color="#6f4e37", size=30),
            ),
        )

        self.customer_marker = ftm.Marker(
            coordinates=ftm.MapLatitudeLongitude(self.initial_latitude, self.initial_longitude),
            content=ft.Container(
                content=ft.Icon(ft.Icons.PERSON_PIN_CIRCLE, color="#1E88E5", size=30),
            ),
            visible=False,
        )

        self.marker_layer = ftm.MarkerLayer(
            markers=[shop_marker, self.customer_marker],
        )

        self.route_polyline = ftm.PolylineMarker(
            coordinates=[
                ftm.MapLatitudeLongitude(SHOP_LATITUDE, SHOP_LONGITUDE),
                ftm.MapLatitudeLongitude(self.initial_latitude, self.initial_longitude),
            ],
            color="#1E88E5",
            stroke_width=4,
        )
        self.route_layer = ftm.PolylineLayer(
            polylines=[self.route_polyline],
            visible=False,
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
                    fallback_url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=self._handle_tile_error,
                ),
                self.route_layer,
                self.marker_layer,
                ftm.SimpleAttribution(
                    text="OpenStreetMap contributors",
                    on_click=on_attribution_click
                )
            ],
        )
        
        # Button to find your location
        my_location_btn = ft.FilledButton(
            content=ft.Text("📍 Customer Location", size=12),
            bgcolor=self.primary_brown,
            color=self.white,
            on_click=self._on_location_click,
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
