import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from deliveries import DeliveriesPage


def main(page: ft.Page):
    page.title = "NomNom - Deliveries"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 900

    # Display deliveries page directly
    deliveries_page = DeliveriesPage(page)
    page.add(deliveries_page.build())


ft.run(main)
