# pastry/urls.py
from django.urls import path
from . import views

app_name = 'pastry'

urlpatterns = [
    path('<str:category>/', views.category_view, name='category_view'),
    path('customize/<str:category>/', views.customize_pastry, name='customize_pastry'),
    #path('add/<int:pastry_id>/', views.add_to_cart, name='add_to_cart'),
]


