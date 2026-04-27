"""
Orders service for the NomNom mobile app.
Handles fetching user orders.
"""

from config import ENDPOINTS
from common.api_client import APIClient
from common.storage import StorageManager
from common.error_handler import NetworkError


class OrdersService:
    """Service for fetching and managing orders."""
    
    def __init__(self, api_client: APIClient, storage: StorageManager):
        """
        Initialize orders service.
        
        Args:
            api_client: APIClient instance
            storage: StorageManager instance
        """
        self.api_client = api_client
        self.storage = storage
    
    def get_orders(
        self,
        status: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """
        Get user orders with optional filtering.
        
        Args:
            status: Filter by order status (pending, paid, cancelled)
            search: Search query
            limit: Max number of orders to return
            offset: Pagination offset
            
        Returns:
            Dictionary with orders list and pagination info
            
        Raises:
            NetworkError: If request fails
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        try:
            response = self.api_client.get(ENDPOINTS["orders"], params=params)

            # Support non-paginated list responses: [...]
            if isinstance(response, list):
                return {
                    "count": len(response),
                    "next": None,
                    "previous": None,
                    "results": response,
                }

            # Paginated response: {"count": X, "next": ..., "previous": ..., "results": [...]}
            if isinstance(response, dict) and "results" in response:
                return response

            # Wrapped responses: {"success": true, "data": ...}
            if isinstance(response, dict) and response.get("success"):
                data = response.get("data", {})
                if isinstance(data, list):
                    return {
                        "count": len(data),
                        "next": None,
                        "previous": None,
                        "results": data,
                    }
                if isinstance(data, dict):
                    return data
            
            raise NetworkError("Failed to fetch orders.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch orders: {str(e)}")
    
    def get_order_detail(self, order_id: int) -> dict:
        """
        Get detailed information about a single order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Dictionary with order details
            
        Raises:
            NetworkError: If request fails
        """
        endpoint = f"{ENDPOINTS['orders']}{order_id}/"
        
        try:
            response = self.api_client.get(endpoint)
            
            # Single order returns OrderSerializer directly (not wrapped)
            if isinstance(response, dict) and "id" in response:
                return response
            
            # Fallback for wrapped responses
            if response.get("success"):
                return response.get("data", {})
            
            raise NetworkError("Failed to fetch order details.")
        except Exception as e:
            raise NetworkError(f"Failed to fetch order details: {str(e)}")
