from django.urls import path
from . import views

# define the application name to avoid Django making confusion down the line
app_name = "landing"

# create inner application routings
urlpatterns = [
    # our default page
    path("", views.index, name="index")
]
