from django.contrib import admin

# WARNING: testing - import our test model
from .models import User

# register the model here
admin.site.register(User)
