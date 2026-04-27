"""
Utility functions for formatting dates and currency values.
Used by various screens to display data consistently.
"""

from datetime import datetime
from typing import Union


def format_currency(amount: Union[str, float, int], currency: str = "$") -> str:
    """
    Format a currency amount for display.
    
    Args:
        amount: The amount to format (string, float, or int)
        currency: Currency symbol (default: "$")
        
    Returns:
        Formatted currency string (e.g., "$15.50")
    """
    try:
        numeric_amount = float(amount)
        return f"{currency}{numeric_amount:.2f}"
    except (ValueError, TypeError):
        return f"{currency}0.00"


def format_date(date_str: str, output_format: str = "%b %d, %Y") -> str:
    """
    Format a date string for display.
    
    Handles ISO format dates (YYYY-MM-DD) or datetime strings.
    
    Args:
        date_str: Date string to format
        output_format: Desired output format (default: "Mar 15, 2024")
        
    Returns:
        Formatted date string
    """
    if not date_str:
        return "N/A"
    
    try:
        # Try parsing ISO format first (YYYY-MM-DD)
        if "T" in date_str:
            # Datetime format with T
            parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            # Date format
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        return parsed_date.strftime(output_format)
    except (ValueError, TypeError):
        # If parsing fails, return the original string
        return date_str


def format_order_status(status: str) -> str:
    """
    Format order status for display.
    
    Args:
        status: Raw status string from API
        
    Returns:
        Formatted status string (title case)
    """
    if not status:
        return "Unknown"
    
    # Map API status values to display format
    status_map = {
        "pending": "Pending",
        "Pending": "Pending",
        "paid": "Paid",
        "Paid": "Paid",
        "cancelled": "Cancelled",
        "Cancelled": "Cancelled",
        "processing": "Processing",
        "Processing": "Processing",
        "delivered": "Delivered",
        "Delivered": "Delivered",
    }
    
    return status_map.get(status, status.title())


def format_delivery_status(status: str) -> str:
    """
    Format delivery status for display.
    
    Args:
        status: Raw delivery status from API
        
    Returns:
        Formatted status string
    """
    if not status:
        return "Unknown"
    
    status_map = {
        "pending": "Pending",
        "Pending": "Pending",
        "done": "Delivered",
        "Done": "Delivered",
        "delivered": "Delivered",
        "Delivered": "Delivered",
        "failed": "Failed",
        "Failed": "Failed",
        "cancelled": "Cancelled",
        "Cancelled": "Cancelled",
    }
    
    return status_map.get(status, status.title())


def get_status_color(status: str, type_: str = "order") -> str:
    """
    Get color for status badge.
    
    Args:
        status: Status string
        type_: Type of status ("order" or "delivery")
        
    Returns:
        Hex color code
    """
    status = format_order_status(status) if type_ == "order" else format_delivery_status(status)
    
    status_colors = {
        "Pending": "#FF9800",      # Orange
        "Paid": "#2196F3",          # Blue
        "Processing": "#2196F3",    # Blue
        "Delivered": "#4CAF50",     # Green
        "Cancelled": "#F44336",     # Red
        "Failed": "#F44336",        # Red
    }
    
    return status_colors.get(status, "#757575")  # Default gray
