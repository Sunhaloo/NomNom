"""
Configuration for the NomNom mobile app.
Contains API endpoints, constants, and shop coordinates.
"""

import os

# API Configuration (can override with NOMNOM_API_URL environment variable)
API_BASE_URL = os.getenv("NOMNOM_API_URL", "http://localhost:8000/api/v1")
API_TIMEOUT = 30  # seconds

# Endpoints
ENDPOINTS = {
    "token": f"{API_BASE_URL}/auth/token/",
    "signup": f"{API_BASE_URL}/auth/signup/",
    "stats": f"{API_BASE_URL}/stats/",
    "reviews": f"{API_BASE_URL}/reviews/top-rated/",
    "profile": f"{API_BASE_URL}/users/me/",
    "orders": f"{API_BASE_URL}/orders/",
    "deliveries": f"{API_BASE_URL}/deliveries/",
    "delivery_confirm": lambda delivery_id: f"{API_BASE_URL}/deliveries/{delivery_id}/confirm-with-photo/",
    "pastries_banner": f"{API_BASE_URL}/pastries/banner/",
}

# Shop Coordinates (for distance/ETA calculations)
SHOP_LATITUDE = -20.2479694
SHOP_LONGITUDE = 57.5937393
SHOP_ADDRESS = "NomNom Pastry Shop, Mauritius"

# Storage Keys
STORAGE_KEYS = {
    "auth_token": "auth_token",
    "user_id": "user_id",
    "username": "username",
    "cache_stats": "cache_stats",
    "cache_reviews": "cache_reviews",
    "cache_timestamp": "cache_timestamp",
}

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour

# Photo Upload Configuration
MAX_PHOTO_SIZE_MB = 5
ALLOWED_PHOTO_TYPES = ["image/jpeg", "image/png"]

# QR Code Configuration
QR_CODE_REQUIRED = True
