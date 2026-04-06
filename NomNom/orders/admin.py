from django.contrib import admin

from .models import Order, OrderDetail


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "order_status",
        "total_amount",
        "order_date",
        "pickup_date",
        "is_preorder",
    ]
    list_filter = ["order_status", "order_date", "is_preorder"]
    search_fields = ["id", "user__username", "user__email"]
    inlines = [OrderDetailInline]


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "pastry", "price", "quantity"]
    search_fields = ["order__id", "pastry__pastry_name"]
