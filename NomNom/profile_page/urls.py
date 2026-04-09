from django.urls import path
from . import views

app_name = "profile_page"

urlpatterns = [
    path("", views.profile_view, name="profile"),
    path("edit/", views.edit_profile, name="edit"),
    path("clear-pfp/", views.clear_profile_pic, name="clear_pfp"),
]
