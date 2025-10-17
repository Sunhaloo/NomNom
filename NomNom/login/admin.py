from django.contrib import admin

# import our "class" definition / tables from model
from .models import User

# Register your models here.
admin.site.register(User)
