import flet as ft
from auth.auth_service import AuthService
from common.error_handler import get_user_friendly_message, AuthenticationError, ValidationError, NetworkError


class LoginScreen:
    """Login screen with username/password form."""
    
    def __init__(self, auth_service: AuthService, on_login_success, show_notification, router=None):
    
        self.auth_service = auth_service
        self.on_login_success = on_login_success
        self.show_notification = show_notification
        self.router = router
        
        # Color scheme from CSS
        self.primary_brown = "#8D6E63"
        self.cream_bg = "#FFF8E1"
        self.text_dark = "#3E2723"
        self.btn_primary = "#000000"
        self.white = "#ffffff"
        
        # Form fields
        self.username_field = ft.TextField(
            label="Username",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=50,
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=50,
        )
        
        self.login_btn = ft.FilledButton(
            content=ft.Text("Login"),
            bgcolor=self.btn_primary,
            color=self.white,
            height=50,
            width=300,
            on_click=self._handle_login,
        )
        
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=self.primary_brown,
        )
    
    def _handle_login(self, e):
        """Handle login button click."""
        username = self.username_field.value.strip()
        password = self.password_field.value.strip()
        
        if not username or not password:
            self.show_notification("Please enter username and password.", error=True)
            return
        
        # Show loading
        self.login_btn.disabled = True
        self.loading_indicator.visible = True
        try:
            self.login_btn.update()
            self.loading_indicator.update()
        except RuntimeError:
            # Control not yet added to page, skip update
            pass
        
        try:
            result = self.auth_service.login(username, password)
            self.show_notification("Login successful!", error=False)
            self.on_login_success(result)
        except (AuthenticationError, ValidationError, NetworkError) as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.login_btn.disabled = False
            self.loading_indicator.visible = False
            try:
                self.login_btn.update()
                self.loading_indicator.update()
            except RuntimeError:
                # Control not yet added to page, skip update
                pass
    
    def build(self) -> ft.Container:
        """Build and return login screen UI."""
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=40),  # Spacer
                    
                    # Title
                    ft.Text(
                        "NomNom",
                        size=36,
                        weight="bold",
                        color=self.text_dark,
                    ),
                    
                    ft.Text(
                        "Welcome Back",
                        size=18,
                        color=self.primary_brown,
                    ),
                    
                    ft.Container(height=30),  # Spacer
                    
                    # Form container
                    ft.Container(
                        width=300,
                        content=ft.Column(
                            controls=[
                                self.username_field,
                                self.password_field,
                                
                                ft.Container(height=20),
                                
                                self.login_btn,
                                
                                ft.Container(height=10),
                                
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("Don't have an account? ", size=13),
                                        ft.TextButton(
                                            content=ft.Text("Sign Up"),
                                            on_click=lambda e: self._navigate_to_signup(),
                                        ),
                                    ],
                                ),
                                
                                self.loading_indicator,
                            ],
                            spacing=12,
                        ),
                    ),
                ],
                spacing=10,
            ),
        )
    
    def _navigate_to_signup(self, e=None):
        if self.router:
            self.router.navigate("signup")
        else:
            self.show_notification("Navigation not available", error=True)
