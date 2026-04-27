"""
Delivery confirmation screen - take a photo to prove delivery
"""

import flet as ft
from deliveries.deliveries_service import DeliveriesService
from common.error_handler import get_user_friendly_message, PhotoUploadError, NetworkError


class DeliveryConfirmationScreen:
    """Screen to confirm a delivery by taking a photo"""
    
    def __init__(
        self,
        deliveries_service: DeliveriesService,
        delivery_id: int,
        on_confirm_success,
        on_cancel,
        show_notification,
    ):
        """Set up the confirmation screen"""
        self.deliveries_service = deliveries_service
        self.delivery_id = delivery_id
        self.on_confirm_success = on_confirm_success
        self.on_cancel = on_cancel
        self.show_notification = show_notification
        
        # Colors
        self.primary_brown = "#8D6E63"
        self.light_brown = "#D7CCC8"
        self.lighter_brown = "#EFEBE9"
        self.text_dark = "#3E2723"
        self.text_light = "#5D4037"
        self.white = "#ffffff"
        
        # Camera setup
        self.camera = ft.CameraPreview(
            on_loaded=self._on_camera_loaded,
        )
        self.photo_path = None
        self.is_camera_ready = False
        
        # UI components
        self.camera_container = ft.Container(
            bgcolor=self.text_dark,
            border_radius=10,
            overflow=ft.ClipBehavior.HARD_EDGE,
            content=self.camera,
        )
        
        self.photo_preview = ft.Image(
            visible=False,
            width=300,
            height=300,
            fit=ft.ImageFit.COVER,
            border_radius=10,
        )
        
        self.capture_btn = ft.IconButton(
            icon=ft.Icons.CAMERA,
            icon_size=40,
            icon_color=self.white,
            bgcolor=self.primary_brown,
            on_click=self._on_capture_click,
        )
        
        self.retake_btn = ft.FilledButton(
            content=ft.Text("Retake Photo"),
            bgcolor=self.lighter_brown,
            color=self.text_dark,
            visible=False,
            on_click=self._on_retake_click,
        )
        
        self.confirm_btn = ft.FilledButton(
            content=ft.Text("Confirm Delivery"),
            bgcolor=self.primary_brown,
            color=self.white,
            visible=False,
            height=50,
            on_click=self._on_confirm_delivery,
        )
        
        self.cancel_btn = ft.FilledButton(
            content=ft.Text("Cancel"),
            bgcolor=self.lighter_brown,
            color=self.text_dark,
            height=50,
            on_click=lambda e: self.on_cancel(),
        )
        
        self.loading_indicator = ft.ProgressRing(
            color=self.primary_brown,
            visible=False,
        )
    
    def _on_camera_loaded(self):
        """Camera is ready to use"""
        self.is_camera_ready = True
    
    def _on_capture_click(self, e):
        """Take a photo when capture button is clicked"""
        if self.is_camera_ready:
            self.photo_path = self.camera.take_picture()
            if self.photo_path:
                self.photo_preview.src = self.photo_path
                self.photo_preview.visible = True
                self.camera_container.visible = False
                self.retake_btn.visible = True
                self.confirm_btn.visible = True
                self.capture_btn.visible = False
                
                # Update UI
                self.photo_preview.update()
                self.camera_container.update()
                self.retake_btn.update()
                self.confirm_btn.update()
                self.capture_btn.update()
    
    def _on_retake_click(self, e):
        """Go back to camera to take another photo"""
        self.photo_path = None
        self.photo_preview.visible = False
        self.camera_container.visible = True
        self.retake_btn.visible = False
        self.confirm_btn.visible = False
        self.capture_btn.visible = True
        
        # Update UI
        self.photo_preview.update()
        self.camera_container.update()
        self.retake_btn.update()
        self.confirm_btn.update()
        self.capture_btn.update()
    
    def _on_confirm_delivery(self, e):
        """Upload photo and confirm the delivery"""
        if not self.photo_path:
            self.show_notification("Please take a photo first.", error=True)
            return
        
        # Show loading
        self.confirm_btn.disabled = True
        self.loading_indicator.visible = True
        self.confirm_btn.update()
        self.loading_indicator.update()
        
        try:
            result = self.deliveries_service.confirm_delivery_with_photo(
                self.delivery_id,
                self.photo_path,
            )
            self.show_notification("Delivery confirmed successfully!", error=False)
            self.on_confirm_success(result)
        except (PhotoUploadError, NetworkError) as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.confirm_btn.disabled = False
            self.loading_indicator.visible = False
            self.confirm_btn.update()
            self.loading_indicator.update()
    
    def build(self) -> ft.Container:
        """Create the confirmation screen UI"""
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(height=20),
                    
                    # Header
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Text(
                            "Confirm Delivery",
                            size=24,
                            weight="bold",
                            color=self.text_dark,
                        ),
                    ),
                    
                    ft.Container(height=10),
                    
                    # Instructions
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Text(
                            "Take a photo of the delivery with QR code visible for validation.",
                            size=13,
                            color=self.text_light,
                        ),
                    ),
                    
                    ft.Container(height=20),
                    
                    # Show camera or preview
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        padding=ft.padding.symmetric(horizontal=15),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.camera_container,
                                self.photo_preview,
                            ],
                        ),
                    ),
                    
                    ft.Container(height=20),
                    
                    # Camera button in center
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=self.capture_btn,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Bottom action buttons
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=15),
                        content=ft.Column(
                            controls=[
                                self.retake_btn,
                                self.loading_indicator,
                                self.confirm_btn,
                                self.cancel_btn,
                            ],
                            spacing=10,
                        ),
                    ),
                    
                    ft.Container(expand=True),  # Spacer to push content up
                ],
                spacing=0,
            ),
        )
