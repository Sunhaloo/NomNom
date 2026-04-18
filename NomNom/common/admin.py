"""
Admin configuration for common app
"""
from django.contrib import admin
from common.models import SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for site configuration"""
    fields = ('total_app_downloads',)
    list_display = ('id', 'total_app_downloads', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
