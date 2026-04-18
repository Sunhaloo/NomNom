"""
Common models for site-wide configuration
"""
from django.db import models


class SiteConfiguration(models.Model):
    """Store site-wide configurable statistics"""
    total_app_downloads = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return f"Site Config - Downloads: {self.total_app_downloads}"
