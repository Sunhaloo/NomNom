from django.db import models
from django.contrib.auth.models import AbstractUser

# Final unified custom User model
class User(AbstractUser):
    # fields created by your friend
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female")])
    region = models.CharField(max_length=80)
    street = models.CharField(max_length=120)

    # custom role field
    role = models.CharField(max_length=20, default="CUSTOMER")

    # your additional field
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # override save to set role for admins
    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.role = "ADMIN"
        super().save(*args, **kwargs)
