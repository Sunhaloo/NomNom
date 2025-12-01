from django.db import models
from django.conf import settings
from pastry.models import Pastry

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    order_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Paid", "Paid")],
        default="Pending"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_preorder = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_id.username}"

    def calculate_total(self):
        total = sum(detail.price * detail.quantity for detail in self.orderdetails.all())
        self.total_amount = total
        self.save()
        return total


class OrderDetail(models.Model):
    order_detail_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, related_name="orderdetails", on_delete=models.CASCADE)
    pastry_id = models.ForeignKey(Pastry, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.pastry_id.pastry_name} (Order {self.order_id.order_id})"
