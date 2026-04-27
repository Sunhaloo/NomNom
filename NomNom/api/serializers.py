from django.contrib.auth import get_user_model

from rest_framework import serializers

from orders.models import Order, OrderDetail
from delivery.models import Delivery


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for individual order detail items (pastries in an order).
    Returns pastry information with quantity and price.
    """
    pastry_name = serializers.CharField(source='pastry.pastry_name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        """Calculate subtotal: quantity × price"""
        return str(obj.quantity * obj.price)

    class Meta:
        model = OrderDetail
        fields = [
            "id",
            "pastry_name",
            "quantity",
            "price",
            "subtotal",
        ]


class OrderSerializer(serializers.ModelSerializer):
    delivery = serializers.SerializerMethodField()
    items = OrderDetailSerializer(source='order_details', many=True, read_only=True)

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
            "tax_amount",
            "delivery_fee",
            "is_preorder",
            "delivery",
            "items",
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
