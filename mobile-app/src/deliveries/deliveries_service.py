"""
Deliveries service for the NomNom mobile app.
Handles fetching deliveries and confirming delivery with photo.
"""

from pathlib import Path
from config import ENDPOINTS, MAX_PHOTO_SIZE_MB
from common.api_client import APIClient
from common.storage import StorageManager
from common.error_handler import NetworkError, PhotoUploadError, ValidationError


class DeliveriesService:
    """Service for managing deliveries and photo uploads."""
    
    def __init__(self, api_client: APIClient, storage: StorageManager):
        """
        Initialize deliveries service.
        
        Args:
            api_client: APIClient instance
            storage: StorageManager instance
        """
        self.api_client = api_client
        self.storage = storage
    
    def get_deliveries(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """
        Get user deliveries with optional filtering.
        
        Args:
            status: Filter by status (pending, in_transit, delivered, cancelled)
            limit: Max number of deliveries to return
            offset: Pagination offset
            
        Returns:
            Dictionary with deliveries list and pagination info
            
        Raises:
            NetworkError: If request fails
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if status:
            params["status"] = status
        
        try:
            response = self.api_client.get(ENDPOINTS["deliveries"], params=params)
            
            if response.get("success"):
                return response.get("data", {})
            
            raise NetworkError("Failed to fetch deliveries.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch deliveries: {str(e)}")
    
    def get_delivery_detail(self, delivery_id: int) -> dict:
        """
        Get detailed information about a single delivery.
        
        Args:
            delivery_id: Delivery ID
            
        Returns:
            Dictionary with delivery details
            
        Raises:
            NetworkError: If request fails
        """
        endpoint = f"{ENDPOINTS['deliveries']}{delivery_id}/"
        
        try:
            response = self.api_client.get(endpoint)
            
            if response.get("success"):
                return response.get("data", {})
            
            raise NetworkError("Failed to fetch delivery details.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch delivery details: {str(e)}")
    
    def confirm_delivery_with_photo(
        self,
        delivery_id: int,
        photo_path: str,
    ) -> dict:
        """
        Confirm delivery by uploading photo proof.
        
        Args:
            delivery_id: Delivery ID
            photo_path: Path to photo file
            
        Returns:
            Dictionary with confirmation result
            
        Raises:
            ValidationError: If photo is invalid
            PhotoUploadError: If upload fails
            NetworkError: If request fails
        """
        photo_file = Path(photo_path)
        
        # Validate photo exists
        if not photo_file.exists():
            raise ValidationError(f"Photo file not found: {photo_path}")
        
        # Validate file size
        file_size_mb = photo_file.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_PHOTO_SIZE_MB:
            raise ValidationError(
                f"Photo size exceeds {MAX_PHOTO_SIZE_MB}MB limit."
            )
        
        try:
            endpoint = ENDPOINTS["delivery_confirm"](delivery_id)
            
            with open(photo_file, "rb") as f:
                files = {"confirmation_photo": f}
                response = self.api_client.post(
                    endpoint,
                    files=files,
                    require_auth=True,
                )
            
            if not response.get("success"):
                raise PhotoUploadError(
                    response.get("message", "Failed to confirm delivery.")
                )
            
            return response.get("data", {})
        except (PhotoUploadError, NetworkError):
            raise
        except Exception as e:
            raise PhotoUploadError(f"Failed to upload photo: {str(e)}")
    
    def calculate_distance(
        self,
        user_latitude: float,
        user_longitude: float,
        shop_latitude: float,
        shop_longitude: float,
    ) -> float:
        """
        Calculate distance between user and shop using Haversine formula.
        
        Args:
            user_latitude: User latitude
            user_longitude: User longitude
            shop_latitude: Shop latitude
            shop_longitude: Shop longitude
            
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1, lon1 = radians(user_latitude), radians(user_longitude)
        lat2, lon2 = radians(shop_latitude), radians(shop_longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def estimate_eta_minutes(
        self,
        distance_km: float,
        speed_kmh: float = 25,
    ) -> int:
        """
        Estimate delivery ETA based on distance and speed.
        
        Args:
            distance_km: Distance in kilometers
            speed_kmh: Average speed in km/h
            
        Returns:
            Estimated time in minutes
        """
        return int((distance_km / speed_kmh) * 60)
