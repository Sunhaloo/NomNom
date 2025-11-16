# pastry/urls.py
from django.urls import path
from . import views

app_name = 'pastry'

urlpatterns = [
    path('customize/', views.customize_pastry, name='customize_pastry'),
    path('<str:category>/', views.category_view, name='category_view'),
]

