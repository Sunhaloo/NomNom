from django.db import models
from django.contrib.auth.models import AbstractUser


# Inheriting from existing default admin class
# adding additional fields
class User(AbstractUser):
    # # store "M", show "Male". Django treats input as a dropdown
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female")])
    region = models.CharField(max_length=80)
    street = models.CharField(max_length=120)
    role = models.CharField(max_length=20, default="CUSTOMER")

    # overriding role for users who are staff/superuser
    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.role = "ADMIN"
        super().save(*args, **kwargs)
