from django.contrib import admin

# WARNING: testing - import our test model
from .models import Test

# register the model here
admin.site.register(Test)
