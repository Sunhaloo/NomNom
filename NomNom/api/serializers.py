from django.contrib.auth import get_user_model

from rest_framework import serializers

from orders.models import Order
from delivery.models import Delivery


class OrderSerializer(serializers.ModelSerializer):
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