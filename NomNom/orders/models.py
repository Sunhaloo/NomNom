from django.db import models
from django.contrib.auth import get_user_model
from pastry.models import Pastry

User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        return f"Order #{self.id} - {self.user.username}"

    def calculate_total(self):
        total = sum(detail.price * detail.quantity for detail in self.order_details.all())
        self.total_amount = total
        self.save()
        return total


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    pastry = models.ForeignKey(Pastry, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.pastry.pastry_name} (Order #{self.order.id})"
