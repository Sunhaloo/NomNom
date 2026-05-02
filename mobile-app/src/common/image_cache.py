"""
Image caching utility for NomNom mobile app.
Downloads and caches images locally to improve performance and reliability.
"""

import os
import json
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class ImageCache:
    """Manages image caching for the mobile app."""
    
    # Cache directory (within .nomnom_data)
    CACHE_DIR = Path.home() / ".nomnom_data" / "images"
    MANIFEST_FILE = Path.home() / ".nomnom_data" / "image_manifest.json"
    
    # Cache expiration time (24 hours)
    CACHE_TTL_HOURS = 24
    
    @staticmethod
    def ensure_cache_dir() -> None:
        """Create cache directory if it doesn't exist."""
        ImageCache.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def load_manifest() -> dict:
        """Load cache manifest file."""
        try:
            if ImageCache.MANIFEST_FILE.exists():
                with open(ImageCache.MANIFEST_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[ImageCache] Error loading manifest: {e}")
        
        return {"images": {}, "last_updated": None}
    
    @staticmethod
    def save_manifest(manifest: dict) -> None:
        """Save cache manifest file."""
        try:
            ImageCache.ensure_cache_dir()
            with open(ImageCache.MANIFEST_FILE, 'w') as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            print(f"[ImageCache] Error saving manifest: {e}")
    
    @staticmethod
    def is_cache_expired(cache_key: str) -> bool:
        """Check if a cached image has expired."""
        manifest = ImageCache.load_manifest()
        
        if cache_key not in manifest["images"]:
            return True  # Not in cache yet
        
        cached_entry = manifest["images"][cache_key]
        downloaded_time = datetime.fromisoformat(cached_entry["downloaded_at"])
        expiry_time = downloaded_time + timedelta(hours=ImageCache.CACHE_TTL_HOURS)
        
        return datetime.now() > expiry_time
    
    @staticmethod
    def get_cache_dir() -> Path:
        """
        Get cache directory path for current user.
        Works universally across different machines/users.
        
        Returns:
            Path object pointing to ~/.nomnom_data/images/
        """
        return Path.home() / ".nomnom_data" / "images"
    
    @staticmethod
    def get_cache_path(cache_key: str) -> Path:
        """Get the full file path for a cached image."""
        return ImageCache.get_cache_dir() / f"{cache_key}.jpg"
    
    @staticmethod
    def is_cached(cache_key: str) -> bool:
        """Check if image exists in cache and is not expired."""
        cache_path = ImageCache.get_cache_path(cache_key)
        
        if not cache_path.exists():
            return False
        
        if ImageCache.is_cache_expired(cache_key):
            return False
        
        return True
    
    @staticmethod
    def download_and_cache_image(image_url: str, cache_key: str) -> Optional[str]:
        """
        Download image from URL and cache it locally.
        Returns relative filename for use with get_cache_dir().
        
        Args:
            image_url: Full URL to download image from
            cache_key: Unique key for caching (e.g., "pastry_1", "logo")
            
        Returns:
            Filename (e.g., "pastry_1.jpg") if successful, None if failed
        """
        if not image_url:
            print(f"[ImageCache] Empty URL for cache_key: {cache_key}")
            return None
        
        try:
            ImageCache.ensure_cache_dir()
            
            cache_path = ImageCache.get_cache_path(cache_key)
            
            print(f"[ImageCache] Downloading image: {image_url}")
            print(f"[ImageCache] Saving to: {cache_path}")
            
            # Download image
            urllib.request.urlretrieve(image_url, cache_path)
            
            # Update manifest
            manifest = ImageCache.load_manifest()
            manifest["images"][cache_key] = {
                "url": image_url,
                "path": str(cache_path),
                "downloaded_at": datetime.now().isoformat(),
            }
            manifest["last_updated"] = datetime.now().isoformat()
            ImageCache.save_manifest(manifest)
            
            print(f"[ImageCache] Successfully cached: {cache_key}")
            # Return just the filename
            filename = f"{cache_key}.jpg"
            return filename
            
        except Exception as e:
            print(f"[ImageCache] Error downloading {image_url}: {e}")
            return None
    
    @staticmethod
    def get_cached_image(image_url: str, cache_key: str) -> Optional[str]:
        """
        Get cached image path, downloading if necessary.
        Returns absolute file path for use in Flet Image widgets.
        
        Args:
            image_url: Full URL to download if not cached
            cache_key: Unique key for caching
            
        Returns:
            Absolute file path if available, None if unavailable and download failed
        """
        if not image_url or not cache_key:
            return None
        
        # Check if already cached and not expired
        if ImageCache.is_cached(cache_key):
            cache_path = ImageCache.get_cache_path(cache_key)
            if cache_path.exists():
                print(f"[ImageCache] Using cached image: {cache_key}")
                # Return absolute path (no file:// prefix - Flet handles Path objects)
                return str(cache_path)
        
        # Download if not cached
        print(f"[ImageCache] Cache miss for {cache_key}, downloading...")
        cached_filename = ImageCache.download_and_cache_image(image_url, cache_key)
        if cached_filename:
            # Return absolute path using cache directory
            return str(ImageCache.get_cache_dir() / cached_filename)
        return None
    
    @staticmethod
    def cache_logo_from_assets() -> Optional[str]:
        """
        Cache logo from assets directory.
        Copy logo from assets to cache on first run.
        Returns absolute file path for use in Flet Image widgets.
        
        Returns:
            Absolute path to cached logo, None if failed
        """
        try:
            ImageCache.ensure_cache_dir()
            
            assets_logo = Path(__file__).parent.parent / "assets" / "NomNom-Logo.png"
            cache_logo = ImageCache.get_cache_path("logo")
            
            if not assets_logo.exists():
                print(f"[ImageCache] Logo not found in assets: {assets_logo}")
                return None
            
            # Copy logo to cache
            if not cache_logo.exists():
                shutil.copy(assets_logo, cache_logo)
                print(f"[ImageCache] Logo cached from assets")
            
            # Update manifest
            manifest = ImageCache.load_manifest()
            manifest["images"]["logo"] = {
                "url": "assets",
                "path": str(cache_logo),
                "downloaded_at": datetime.now().isoformat(),
            }
            ImageCache.save_manifest(manifest)
            
            # Return absolute path (no file:// prefix - Flet handles Path objects)
            return str(cache_logo)
            
        except Exception as e:
            print(f"[ImageCache] Error caching logo: {e}")
            return None
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached images."""
        try:
            if ImageCache.CACHE_DIR.exists():
                shutil.rmtree(ImageCache.CACHE_DIR)
                ImageCache.MANIFEST_FILE.unlink(missing_ok=True)
                print("[ImageCache] Cache cleared")
        except Exception as e:
            print(f"[ImageCache] Error clearing cache: {e}")
    
    @staticmethod
    def get_cache_size() -> int:
        """Get total size of cached images in bytes."""
        if not ImageCache.CACHE_DIR.exists():
            return 0
        
        total_size = 0
        for file_path in ImageCache.CACHE_DIR.iterdir():
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
