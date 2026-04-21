"""
Map Demo - Test script to view the map without authentication
Run this to see your map implementation working!
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import flet as ft
from deliveries.screens.map_screen import MapScreen


def main(page: ft.Page):
    """Test map directly."""
    page.title = "NomNom - Map Test"
    page.window.width = 400
    page.window.height = 800
    page.padding = 0
    page.margin = 0
    
    # Create map screen
    def go_back():
        page.clean()
        page.add(
            ft.Container(
                expand=True,
                bgcolor="#ffffff",
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        ft.Text("Map Demo", size=28, weight="bold"),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Show Map",
                            on_click=lambda e: show_map()
                        ),
                    ]
                ),
            )
        )
    
    def show_map():
        map_screen = MapScreen(on_back=go_back)
        page.clean()
        page.add(map_screen.build())
    
    # Show initial screen
    page.add(
        ft.Container(
            expand=True,
            bgcolor="#ffffff",
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Text("Map Demo", size=28, weight="bold", color="#3E2723"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Click to View Map",
                        on_click=lambda e: show_map(),
                        bgcolor="#8D6E63",
                        color="#ffffff",
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "This demonstrates your map implementation",
                        size=12,
                        color="#5D4037"
                    ),
                ]
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
