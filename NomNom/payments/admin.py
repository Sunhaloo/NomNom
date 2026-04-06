from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_id",
        "order",
        "payment_status",
        "payment_method",
        "amount",
        "payment_date",
    ]
    list_filter = ["payment_status", "payment_method", "payment_date"]
    search_fields = ["payment_id", "order__id"]
