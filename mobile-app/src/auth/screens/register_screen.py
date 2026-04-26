"""
Registration/Signup screen for the NomNom mobile app.
"""

import flet as ft
from auth.auth_service import AuthService
from common.error_handler import get_user_friendly_message, AuthenticationError, ValidationError, NetworkError


class RegisterScreen:
    """Registration screen with full form."""
    
    def __init__(self, auth_service: AuthService, on_signup_success, show_notification, router=None):
        """
        Initialize register screen.
        
        Args:
            auth_service: AuthService instance
            on_signup_success: Callback when signup succeeds
            show_notification: Function to show error/success notifications
            router: Router instance for navigation
        """
        self.auth_service = auth_service
        self.on_signup_success = on_signup_success
        self.show_notification = show_notification
        self.router = router
        
        # Color scheme
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
            height=45,
        )
        
        self.email_field = ft.TextField(
            label="Email",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
        )
        
        self.first_name_field = ft.TextField(
            label="First Name",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
        )
        
        self.last_name_field = ft.TextField(
            label="Last Name",
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            password=True,
            border_color=self.primary_brown,
            focused_border_color=self.primary_brown,
            text_size=14,
            height=45,
        )
        
        self.signup_btn = ft.FilledButton(
            content=ft.Text("Sign Up"),
            bgcolor=self.btn_primary,
            color=self.white,
            height=50,
            width=300,
            on_click=self._handle_signup,
        )
        
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=self.primary_brown,
        )
    
    def _validate_inputs(self) -> tuple[bool, str]:
        """
        Validate form inputs.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        username = self.username_field.value.strip()
        email = self.email_field.value.strip()
        first_name = self.first_name_field.value.strip()
        last_name = self.last_name_field.value.strip()
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value
        
        if not all([username, email, first_name, last_name, password, confirm_password]):
            return False, "All fields are required."
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        
        if password != confirm_password:
            return False, "Passwords do not match."
        
        if "@" not in email:
            return False, "Please enter a valid email."
        
        return True, ""
    
    def _handle_signup(self, e):
        """Handle signup button click."""
        is_valid, error_msg = self._validate_inputs()
        
        if not is_valid:
            self.show_notification(error_msg, error=True)
            return
        
        # Show loading
        self.signup_btn.disabled = True
        self.loading_indicator.visible = True
        self.signup_btn.update()
        self.loading_indicator.update()
        
        try:
            result = self.auth_service.signup(
                username=self.username_field.value.strip(),
                password=self.password_field.value,
                email=self.email_field.value.strip(),
                first_name=self.first_name_field.value.strip(),
                last_name=self.last_name_field.value.strip(),
            )
            self.show_notification("Sign up successful!", error=False)
            self.on_signup_success(result)
        except (AuthenticationError, ValidationError, NetworkError) as e:
            self.show_notification(get_user_friendly_message(e), error=True)
        finally:
            self.signup_btn.disabled = False
            self.loading_indicator.visible = False
            self.signup_btn.update()
            self.loading_indicator.update()
    
    def build(self) -> ft.Container:
        """Build and return signup screen UI."""
        return ft.Container(
            expand=True,
            bgcolor=self.white,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(height=20),  # Spacer
                    
                    # Title
                    ft.Text(
                        "NomNom",
                        size=36,
                        weight="bold",
                        color=self.text_dark,
                    ),
                    
                    ft.Text(
                        "Create Account",
                        size=18,
                        color=self.primary_brown,
                    ),
                    
                    # Scrollable form
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Container(height=20),
                                
                                # Form fields
                                ft.Container(
                                    width=300,
                                    content=ft.Column(
                                        controls=[
                                            self.username_field,
                                            self.email_field,
                                            self.first_name_field,
                                            self.last_name_field,
                                            self.password_field,
                                            self.confirm_password_field,
                                            
                                            ft.Container(height=15),
                                            
                                            self.signup_btn,
                                            
                                            ft.Container(height=10),
                                            
                                            ft.Row(
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Text("Already have an account? ", size=13),
                                                    ft.TextButton(
                                                        content=ft.Text("Log In"),
                                                        on_click=lambda e: self._navigate_to_login(),
                                                    ),
                                                ],
                                            ),
                                            
                                            self.loading_indicator,
                                        ],
                                        spacing=10,
                                    ),
                                ),
                            ],
                        ),
                    ),
                    
                    ft.Container(height=20),  # Bottom spacer
                ],
            ),
        )
    
    def _navigate_to_login(self):
        """Navigate to login screen."""
        if self.router:
            self.router.navigate("login")
        else:
            self.show_notification("Navigation not available", error=True)
