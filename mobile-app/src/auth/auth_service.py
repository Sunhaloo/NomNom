"""
Authentication service for the NomNom mobile app.
Handles login, signup, and logout operations.
"""

from common.logger import logger
from config import ENDPOINTS
from common.api_client import APIClient
from common.storage import StorageManager
from common.error_handler import (
    AuthenticationError,
    ValidationError,
    NetworkError,
)


class AuthService:
    """Service for handling user authentication."""

    def __init__(self, api_client: APIClient, storage: StorageManager):
        """
        Initialize auth service.

        Args:
            api_client: APIClient instance
            storage: StorageManager instance
        """
        self.api_client = api_client
        self.storage = storage

    def login(self, username: str, password: str) -> dict:
        if not username or not password:
            logger.warning("Login attempt with empty credentials")
            raise ValidationError("Username and password are required.")

        try:
            logger.debug("Login attempt", username=username)
            result = self.api_client.post(
                ENDPOINTS["token"],
                json={"username": username, "password": password},
                require_auth=False,
            )

            if not result.get("success"):
                raise AuthenticationError(
                    result.get("message")
                    or result.get("error")
                    or "Login failed."
                )

            token = result.get("data", {}).get("token")
            user_id = result.get("data", {}).get("user", {}).get("id")
            if token and user_id:
                self.storage.save_token(token, user_id, username)

            logger.info("Login successful", username=username)
            return {"success": True, "data": result.get("data", {})}
        except (AuthenticationError, NetworkError) as e:
            logger.error("Login failed", username=username, error=str(e))
            raise
    def signup(
        self,
        username: str,
        password: str,
        email: str,
        first_name: str,
        last_name: str,
        phone_number: str = "",
    ) -> dict:
        """
        Register new user.

        Args:
            username: Username
            password: Password
            email: Email address
            first_name: First name
            last_name: Last name
            phone_number: Phone number (optional)

        Returns:
            Dictionary with user info and token

        Raises:
            ValidationError: If inputs are invalid
            AuthenticationError: If signup fails
            NetworkError: If request fails
        """
        if not all([username, password, email, first_name, last_name]):
            raise ValidationError("All fields are required.")

        try:
            signup_data = {
                "username": username,
                "password": password,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
            
            # Add phone_number if provided
            if phone_number:
                signup_data["phone_number"] = phone_number
            
            response = self.api_client.post(
                ENDPOINTS["signup"],
                json=signup_data,
                require_auth=False,
            )

            if not response.get("success"):
                raise AuthenticationError(response.get("message", "Signup failed."))

            token = response["data"]["token"]
            user_id = response["data"]["user"]["id"]

            self.storage.save_token(token, user_id, username)

            return {
                "success": True,
                "token": token,
                "user": response["data"]["user"],
            }
        except (AuthenticationError, NetworkError):
            raise
        except Exception as e:
            raise AuthenticationError(f"Signup failed: {str(e)}")

    def logout(self) -> None:
        """
        Logout current user.

        Raises:
            AuthenticationError: If not logged in
        """
        token_data = self.storage.load_token()
        if not token_data:
            raise AuthenticationError("Not logged in.")

        self.storage.clear_token()
        self.storage.clear_cache()

    def is_logged_in(self) -> bool:
        """
        Check if user is logged in.

        Returns:
            True if user has valid token, False otherwise
        """
        token_data = self.storage.load_token()
        return bool(token_data and token_data.get("auth_token"))

    def get_current_user(self) -> dict | None:
        """
        Get current logged-in user info.

        Returns:
            Dictionary with user info, or None if not logged in
        """
        token_data = self.storage.load_token()
        if not token_data:
            return None

        return {
            "user_id": token_data.get("user_id"),
            "username": token_data.get("username"),
        }
