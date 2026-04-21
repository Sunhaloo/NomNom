"""
Local storage management for the NomNom mobile app.
Handles token persistence, user info, and cache data.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from config import STORAGE_KEYS, CACHE_TTL_SECONDS
from common.error_handler import StorageError


class StorageManager:
    """Manages local file-based storage for auth tokens and cache."""
    
    def __init__(self, storage_dir: str = ".nomnom_data"):
        """
        Initialize storage manager.
        
        Args:
            storage_dir: Directory for storing data files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.token_file = self.storage_dir / "token.json"
        self.cache_file = self.storage_dir / "cache.json"
    
    def save_token(self, token: str, user_id: int, username: str) -> None:
        """
        Save authentication token and user info.
        
        Args:
            token: Authentication token
            user_id: User ID
            username: Username
            
        Raises:
            StorageError: If save operation fails
        """
        try:
            data = {
                STORAGE_KEYS["auth_token"]: token,
                STORAGE_KEYS["user_id"]: user_id,
                STORAGE_KEYS["username"]: username,
                "saved_at": datetime.now().isoformat(),
            }
            with open(self.token_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            raise StorageError(f"Failed to save token: {str(e)}")
    
    def load_token(self) -> dict | None:
        """
        Load authentication token and user info.
        
        Returns:
            Dictionary with token and user info, or None if not found
            
        Raises:
            StorageError: If load operation fails
        """
        try:
            if not self.token_file.exists():
                return None
            with open(self.token_file, "r") as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load token: {str(e)}")
    
    def clear_token(self) -> None:
        """
        Clear stored authentication token.
        
        Raises:
            StorageError: If clear operation fails
        """
        try:
            if self.token_file.exists():
                self.token_file.unlink()
        except Exception as e:
            raise StorageError(f"Failed to clear token: {str(e)}")
    
    def save_cache(self, key: str, data: dict) -> None:
        """
        Save data to cache with timestamp.
        
        Args:
            key: Cache key (e.g., "cache_stats", "cache_reviews")
            data: Data to cache
            
        Raises:
            StorageError: If save operation fails
        """
        try:
            cache = self._load_cache_file() or {}
            cache[key] = {
                "data": data,
                "timestamp": time.time(),
            }
            with open(self.cache_file, "w") as f:
                json.dump(cache, f)
        except Exception as e:
            raise StorageError(f"Failed to save cache: {str(e)}")
    
    def load_cache(self, key: str, ttl_seconds: int = CACHE_TTL_SECONDS) -> dict | None:
        """
        Load data from cache if not expired.
        
        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds
            
        Returns:
            Cached data if valid and not expired, None otherwise
            
        Raises:
            StorageError: If load operation fails
        """
        try:
            cache = self._load_cache_file()
            if not cache or key not in cache:
                return None
            
            cached_item = cache[key]
            age = time.time() - cached_item["timestamp"]
            
            if age > ttl_seconds:
                return None
            
            return cached_item["data"]
        except Exception as e:
            raise StorageError(f"Failed to load cache: {str(e)}")
    
    def clear_cache(self) -> None:
        """
        Clear all cached data.
        
        Raises:
            StorageError: If clear operation fails
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception as e:
            raise StorageError(f"Failed to clear cache: {str(e)}")
    
    def _load_cache_file(self) -> dict | None:
        """
        Internal method to load cache file.
        
        Returns:
            Cache dictionary or None if file doesn't exist
        """
        if not self.cache_file.exists():
            return None
        with open(self.cache_file, "r") as f:
            return json.load(f)
