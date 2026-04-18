from django.db import models
from django.utils import timezone
from orders.models import Order


class Delivery(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending", "Pending"),
            ("Done", "Done"),
            ("Failed", "Failed"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending",
    )
    date = models.DateField()
    
    # Photo confirmation fields for mobile app delivery verification
    confirmation_photo = models.BinaryField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    qr_code_data = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Deliveries"

    def __str__(self):
        return f"Delivery #{self.id} for Order #{self.order.id}"
    
    def save(self, *args, **kwargs):
        """Generate QR code data when created"""
        if not self.qr_code_data:
            self.qr_code_data = f"DELIVERY:{self.id}"
        super().save(*args, **kwargs)
