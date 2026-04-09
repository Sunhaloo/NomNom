from django.contrib import admin

from .models import Pastry


@admin.register(Pastry)
class PastryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "pastry_name",
        "pastry_category",
        "pastry_price",
        "is_custom",
        "is_available",
    ]
    list_filter = ["pastry_category", "is_custom", "is_available"]
    search_fields = ["pastry_name"]
