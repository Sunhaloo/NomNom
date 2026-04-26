from django.contrib.auth import get_user_model

from rest_framework import serializers

from orders.models import Order
from delivery.models import Delivery


class OrderSerializer(serializers.ModelSerializer):
    delivery = serializers.SerializerMethodField()

    def get_delivery(self, obj):
        delivery = (
            Delivery.objects.filter(order=obj)
            .order_by("-id")
            .only("id", "address", "status", "date")
            .first()
        )
        if not delivery:
            return None

        return {
            "id": delivery.id,
            "address": delivery.address,
            "status": delivery.status,
            "date": delivery.date.isoformat() if delivery.date else None,
        }

    class Meta:
        # get the data from the 'order' app
        model = Order
        # fields to be accessible through the API
        fields = [
            "id",
            "order_date",
            "pickup_date",
            "order_status",
            "total_amount",
            "is_preorder",
            "delivery",
        ]


class OrderSummaryForDeliverySerializer(serializers.ModelSerializer):

    class Meta:
        # get the data from the 'order' app
        model = Order
        # fields to be accessible through the API
        fields = [
            "id",
            "order_date",
            "order_status",
            "total_amount",
        ]


class DeliverySerializer(serializers.ModelSerializer):
    order = OrderSummaryForDeliverySerializer(read_only=True)

    class Meta:
        # get the data from the 'delivery' app
        model = Delivery
        # fields to be accessible through the API
        fields = [
            "id",
            "address",
            "date",
            "status",
            "order",
        ]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        # get the data from the 'login_user' table
        model = get_user_model()
        # fields to be accessible through the API
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "street",
            "region",
        ]
