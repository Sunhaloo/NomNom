from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from delivery.models import Delivery
from payments.models import Payment
from .serializers import DeliverySerializer, OrderSerializer, UserProfileSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to list or retrieve orders for the authenticated user.

    - GET /api/v1/orders/: list of the current user's orders
    - GET /api/v1/orders/<id>/: single order (only if it belongs to the user)
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by("-order_date")


class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """Delivery endpoints for the authenticated user.

    - GET /api/v1/deliveries/:
        list of the user's deliveries; by default only Pending ones.
    - GET /api/v1/deliveries/<id>/:
        details for a single delivery (only if it belongs to the user).
    - POST /api/v1/deliveries/<id>/confirm/:
        mark a pending delivery as Done.
    - POST /api/v1/deliveries/<id>/cancel/:
        cancel a pending delivery, cancel the related order, and refund payments.
    """

    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Delivery.objects.select_related("order").filter(order__user=user)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        else:
            qs = qs.filter(status="Pending")

        return qs.order_by("-date", "-id")

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        delivery = self.get_object()

        if delivery.status != "Pending":
            return Response(
                {
                    "success": False,
                    "error": "Only pending deliveries can be confirmed.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery.status = "Done"
        delivery.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "delivery_id": delivery.id,
                "new_status": delivery.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        delivery = self.get_object()
        order = delivery.order

        if delivery.status != "Pending":
            return Response(
                {
                    "success": False,
                    "error": "Only pending deliveries can be cancelled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            delivery.status = "Cancelled"
            delivery.save(update_fields=["status"])

            # Cancel order
            order.order_status = "Cancelled"
            order.save(update_fields=["order_status"])

            # Refund payments for this order
            Payment.objects.filter(order=order, payment_status="Paid").update(
                payment_status="Refunded"
            )

        return Response(
            {
                "success": True,
                "delivery_id": delivery.id,
                "order_id": order.id,
                "order_status": order.order_status,
                "delivery_status": delivery.status,
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    """Read-only profile endpoint for the authenticated user.

    - GET /api/v1/users/me/:
        returns a minimal profile with name and address parts that the
        mobile app can use for things like Google Maps integration.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    """Simple token revocation endpoint for mobile/external clients.

    - POST /api/v1/auth/logout/:
        Deletes all auth tokens for the current user. After this call,
        any previously issued tokens will no longer authenticate.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
