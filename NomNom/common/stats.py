"""
Business statistics calculation utility
Calculates stats dynamically from database
"""
from django.db.models import Count
from django.contrib.auth import get_user_model
from orders.models import Order
from delivery.models import Delivery
from common.models import SiteConfiguration

User = get_user_model()


def get_business_stats():
    """
    Calculate all business statistics dynamically
    
    Returns:
        Dictionary with business metrics
    """
    # Get or create the site configuration (for app downloads)
    config, _ = SiteConfiguration.objects.get_or_create(id=1)
    
    return {
        'total_clients': User.objects.filter(role='CUSTOMER').count(),
        'total_purchases': Order.objects.count(),
        'total_satisfied_clients': User.objects.filter(
            orders__delivery__status='Done'
        ).distinct().count(),
        'total_successful_deliveries': Delivery.objects.filter(
            status='Done'
        ).count(),
        'total_downloads': config.total_app_downloads,
    }
