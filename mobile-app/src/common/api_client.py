"""
HTTP client for the NomNom mobile app.
Handles API requests with automatic token authentication.
"""

import logging
from urllib import response

import requests
from typing import Optional, Dict, Any
from config import API_TIMEOUT, ENDPOINTS
from common.error_handler import NetworkError, AuthenticationError
from common.storage import StorageManager

logger = logging.getLogger(__name__)


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
    
    def _validate_json_response(self, response) -> None:
      """
      Validate that response is JSON before attempting to parse.
      
      Args:
          response: requests.Response object
          
      Raises:
          NetworkError: If response is not JSON content type
      """
      content_type = response.headers.get("Content-Type", "")
      if "application/json" not in content_type:
          response_preview = response.text[:200]
          raise NetworkError(
              f"Expected JSON response but got Content-Type: {content_type}. "
              f"Response preview: {response_preview}..."
          )

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
            self._validate_json_response(response)
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
        
        logger.debug("POST request", endpoint=endpoint, require_auth=require_auth)
        try:
            response = requests.post(
                endpoint,
                data=data,
                json=json,
                files=files,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False,  
            )
  
  # Check for redirects (3xx status codes) 
            if 300 <= response.status_code < 400:
                raise NetworkError(
                    f"Server redirect (HTTP {response.status_code}). "
                    f"Expected JSON API response but got redirect to {response.headers.get('Location', 'unknown')}. "
                    f"Check API configuration or proxy settings."
                )
  
            response.raise_for_status()
            self._validate_json_response(response)
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
            self._validate_json_response(response)
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
            self._validate_json_response(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"PATCH request failed: {str(e)}")
