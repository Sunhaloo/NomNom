from django.urls import path
from . import views

app_name = "review"

urlpatterns = [
    path("get/<int:pastry_id>/", views.get_reviews, name="get_reviews"),
    path("add/<int:pastry_id>/", views.add_review, name="add_review"),
]