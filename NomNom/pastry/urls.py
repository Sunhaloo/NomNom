# pastry/urls.py
from django.urls import path
from . import views

app_name = 'pastry'

urlpatterns = [
    path('customize/', views.customize_pastry, name='customize_pastry'),
    path('login-required/', views.login_required_gate, name='login_required_gate'),
    path('<str:category>/', views.category_view, name='category_view'),
]
