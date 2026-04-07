from rest_framework import serializers

from orders.models import Order


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
