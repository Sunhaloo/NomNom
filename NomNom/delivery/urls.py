from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('', views.delivery_list, name='delivery_list'),
    path('<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    path('<int:delivery_id>/update/', views.update_delivery_status, name='update_delivery_status'),
]