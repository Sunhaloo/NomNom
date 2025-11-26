from django.db import models

# import the abstract user "class" model
from django.contrib.auth.models import AbstractUser


# user-created 'User' "child" class that inherits from the 'AbstractUser' class
class User(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True, null=True)   # NEW
    gender = models.CharField(
        max_length=10,
        choices=[("M", "Male"), ("F", "Female")],
        blank=True,
        null=True
    )
    region = models.CharField(max_length=80)
    street = models.CharField(max_length=120)
    role = models.CharField(max_length=20, default="CUSTOMER")
    profile_pic = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True, default=None
    )  

    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.role = "ADMIN"
        super().save(*args, **kwargs)