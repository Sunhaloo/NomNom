from django.urls import path
from . import views

# define the app name here so that Django does not get confused with URLs
app_name = "login"

urlpatterns = [
    # our login path
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("forgetpassword/", views.forget_passwd, name="forget_passwd"),
    path(
        "reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

]
