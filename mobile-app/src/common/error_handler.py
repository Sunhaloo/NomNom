"""
Error handling for the NomNom mobile app.
Provides standardized error messages and exception classes.
"""


class NomNomError(Exception):
    """Base exception for NomNom mobile app."""
    pass


class AuthenticationError(NomNomError):
    """Raised when authentication fails."""
    pass


class ValidationError(NomNomError):
    """Raised when data validation fails."""
    pass


class NetworkError(NomNomError):
    """Raised when network request fails."""
    pass


class StorageError(NomNomError):
    """Raised when local storage operation fails."""
    pass


class PhotoUploadError(NomNomError):
    """Raised when photo upload fails."""
    pass


def get_user_friendly_message(error: Exception) -> str:
    """
    Convert exception to user-friendly message.
    Sanitizes sensitive information and hides stack traces.
    
    Args:
        error: Exception to convert
        
    Returns:
        User-friendly error message string
    """
    # If we have a specific message (often from server), prefer showing it.
    details = str(error).strip()
    if details and isinstance(
        error,
        (
            AuthenticationError,
            ValidationError,
            PhotoUploadError,
        ),
    ):
        return details

    error_map = {
        AuthenticationError: "Unable to authenticate. Please check your credentials.",
        ValidationError: "Please check your input and try again.",
        NetworkError: "Network connection failed. Please try again later.",
        StorageError: "Local storage error. Please restart the app.",
        PhotoUploadError: "Failed to upload photo. Please try again.",
    }
    
    error_class = type(error)
    return error_map.get(error_class, "Something went wrong. Please try again later.")
