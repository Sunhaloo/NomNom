from django.db import models
from orders.models import Order

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        related_name="payments",  # use plural for reverse relation
        on_delete=models.CASCADE
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Paid", "Paid"),
            ("Failed", "Failed")
        ],
        default="Pending"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("Card", "Card"),
            ("Cash", "Cash"),
            ("Online", "Online")
        ],
        default="Card"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.id} - {self.payment_status}"
