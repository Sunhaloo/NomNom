"""
HTTP client for the NomNom mobile app.
Handles API requests with automatic token authentication.
"""

import requests
from typing import Optional, Dict, Any
from config import API_TIMEOUT, ENDPOINTS
from common.error_handler import NetworkError, AuthenticationError
from common.storage import StorageManager


class APIClient:
    """HTTP client with built-in authentication and error handling."""
    
    def __init__(self, storage: StorageManager):
        """
        Initialize API client.
        
        Args:
            storage: StorageManager instance for token management
        """
        self.storage = storage
        self.timeout = API_TIMEOUT
    
    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get authorization header with token.
        
        Returns:
            Dictionary with Authorization header
            
        Raises:
            AuthenticationError: If no token is stored
        """
        token_data = self.storage.load_token()
        if not token_data or not token_data.get("auth_token"):
            raise AuthenticationError("No authentication token found. Please log in.")
        
        token = token_data["auth_token"]
        return {"Authorization": f"Token {token}"}
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: Full endpoint URL
            params: Query parameters
            require_auth: Whether authentication is required
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkError: If request fails
            AuthenticationError: If authentication fails
        """
        headers = {}
        if require_auth:
            headers.update(self._get_auth_header())
        
        try:
            response = requests.get(
                endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"GET request failed: {str(e)}")
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make POST request to API.
        
        Args:
            endpoint: Full endpoint URL
            data: Form data
            json: JSON data
            files: Files for upload
            require_auth: Whether authentication is required
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkError: If request fails
            AuthenticationError: If authentication fails
        """
        headers = {}
        if require_auth:
            headers.update(self._get_auth_header())
        
        try:
            response = requests.post(
                endpoint,
                data=data,
                json=json,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"POST request failed: {str(e)}")
    
    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make PUT request to API.
        
        Args:
            endpoint: Full endpoint URL
            json: JSON data
            data: Form data
            require_auth: Whether authentication is required
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkError: If request fails
            AuthenticationError: If authentication fails
        """
        headers = {}
        if require_auth:
            headers.update(self._get_auth_header())
        
        try:
            response = requests.put(
                endpoint,
                json=json,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"PUT request failed: {str(e)}")
    
    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make PATCH request to API.
        
        Args:
            endpoint: Full endpoint URL
            json: JSON data
            data: Form data
            require_auth: Whether authentication is required
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkError: If request fails
            AuthenticationError: If authentication fails
        """
        headers = {}
        if require_auth:
            headers.update(self._get_auth_header())
        
        try:
            response = requests.patch(
                endpoint,
                json=json,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"PATCH request failed: {str(e)}")
