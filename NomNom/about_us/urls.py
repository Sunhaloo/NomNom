from django.urls import path
from . import views

# define the app name here so that Django does not get confused with URLs
app_name = "about_us"

urlpatterns = [
    # our login path
    path("", views.index, name="about"),
]
