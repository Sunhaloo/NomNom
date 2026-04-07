from rest_framework import permissions, viewsets

from orders.models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list or retrieve orders for the authenticated user.

    - GET /api/v1/orders/: list of the current user's orders
    - GET /api/v1/orders/<id>/: single order ( only if it belongs to the user )
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by("-order_date")
