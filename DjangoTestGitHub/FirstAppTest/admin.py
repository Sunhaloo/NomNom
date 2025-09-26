from django.contrib import admin
from .models import Question

# register the question table
admin.site.register(Question)
