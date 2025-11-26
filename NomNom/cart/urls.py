from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='cart'),  #view cart
    path('add/', views.add_to_cart_ajax, name='add_to_cart_ajax'),  #AJAX add to cart
    path('update/', views.update_cart_quantity, name='update_cart_quantity'),  #AJAX update quantity
    path('add/<int:pastry_id>/', views.add_to_cart, name='add_to_cart'),  #add a pastry to cart 
    path('remove/<int:index>/', views.remove_from_cart, name='remove_from_cart'),   #remove a pastry from cart
    path('clear/', views.clear_cart, name='clear_cart'), # remove all itmes from cart
]


