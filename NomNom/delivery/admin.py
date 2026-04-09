from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'address', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['id', 'order__id', 'address']
    list_editable = ['status']
    readonly_fields = ['id']