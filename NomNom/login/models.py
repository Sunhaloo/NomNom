from django.db import models

# import the abstract user "class" model
from django.contrib.auth.models import AbstractUser


# user-created 'User' "child" class that inherits from the 'AbstractUser' class
class User(AbstractUser):
    # creation of additional fields for our customised needs
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female")], blank=True, null=True)
    region = models.CharField(max_length=80)
    street = models.CharField(max_length=120)
    role = models.CharField(max_length=20, default="CUSTOMER")

    # Additional fields added by migrations
    full_name = models.CharField(max_length=100, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default=None)

    # overriding role for users who are staff/superuser
    def save(self, *args, **kwargs):
        # check if we have have created a staff or superuser
        if self.is_superuser or self.is_staff:
            # if so ==> set their role to "ADMIN" instead of "CUSTOMER"
            self.role = "ADMIN"

        # save the data to the database
        super().save(*args, **kwargs)
