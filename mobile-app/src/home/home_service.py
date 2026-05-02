"""
Home service for the NomNom mobile app.
Handles fetching business stats, reviews, and user profile.
"""

from config import ENDPOINTS, STORAGE_KEYS, CACHE_TTL_SECONDS
from common.api_client import APIClient
from common.storage import StorageManager
from common.error_handler import NetworkError


class HomeService:
    """Service for fetching home screen data."""
    
    def __init__(self, api_client: APIClient, storage: StorageManager):
        """
        Initialize home service.
        
        Args:
            api_client: APIClient instance
            storage: StorageManager instance
        """
        self.api_client = api_client
        self.storage = storage
    
    def get_business_stats(self, force_refresh: bool = False) -> dict:
        """
        Get business statistics (cached).
        
        Args:
            force_refresh: If True, fetch from server and ignore cache
            
        Returns:
            Dictionary with business stats
            
        Raises:
            NetworkError: If request fails
        """
        if not force_refresh:
            cached = self.storage.load_cache(STORAGE_KEYS["cache_stats"])
            if cached:
                return cached
        
        try:
            response = self.api_client.get(ENDPOINTS["stats"])
            
            if response.get("success"):
                stats = response.get("data", {})
                self.storage.save_cache(STORAGE_KEYS["cache_stats"], stats)
                return stats
            
            raise NetworkError("Failed to fetch stats.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch stats: {str(e)}")
    
    def get_top_reviews(self, force_refresh: bool = False) -> list:
        """
        Get top-rated reviews (cached).
        
        Args:
            force_refresh: If True, fetch from server and ignore cache
            
        Returns:
            List of review dictionaries
            
        Raises:
            NetworkError: If request fails
        """
        if not force_refresh:
            cached = self.storage.load_cache(STORAGE_KEYS["cache_reviews"])
            if cached:
                return cached
        
        try:
            response = self.api_client.get(ENDPOINTS["reviews"])
            
            if response.get("success"):
                reviews = response.get("data", [])
                self.storage.save_cache(STORAGE_KEYS["cache_reviews"], reviews)
                return reviews
            
            raise NetworkError("Failed to fetch reviews.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch reviews: {str(e)}")
    
    def get_user_profile(self) -> dict:
        """
        Get current user profile (not cached).
        
        Returns:
            Dictionary with user profile
            
        Raises:
            NetworkError: If request fails
        """
        try:
            response = self.api_client.get(ENDPOINTS["profile"])
            
            if response.get("success"):
                return response.get("data", {})
            
            raise NetworkError("Failed to fetch profile.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch profile: {str(e)}")
    
    def get_pastries_banner(self) -> list:
        """
        Get pastries for banner carousel (mix of best sellers and random).
        
        Returns:
            List of pastry dictionaries
            
        Raises:
            NetworkError: If request fails
        """
        try:
            response = self.api_client.get(ENDPOINTS["pastries_banner"])
            
            if response.get("success"):
                return response.get("data", [])
            
            raise NetworkError("Failed to fetch pastries.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch pastries: {str(e)}")
