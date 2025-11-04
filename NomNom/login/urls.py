from django.urls import path
from . import views

# define the app name here so that Django does not get confused with URLs
app_name = "login"

urlpatterns = [
    # our login path
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
]
