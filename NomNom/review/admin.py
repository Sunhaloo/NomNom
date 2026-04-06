from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "pastry", "rating", "date"]
    list_filter = ["rating", "date"]
    search_fields = ["user__username", "pastry__pastry_name", "comment"]
