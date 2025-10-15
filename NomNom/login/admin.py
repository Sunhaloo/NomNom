from django.contrib import admin

# import our "class" definition / tables from model
from .models import Test

# Register your models here.
admin.site.register(Test)
