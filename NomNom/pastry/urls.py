from django.urls import path
from . import views

#redirecting to each category of pastry from landing page
urlpatterns = [
    path('cakes/', views.cakes, name='cakes'),
    path('brownies/', views.brownies, name='brownies'),
    path('cookies/', views.cookies, name='cookies'),
    path('cupcakes/', views.cupcakes, name='cupcakes'),
    path('doughnuts/', views.doughnuts, name='doughnuts'),
    path('tarts/', views.tarts, name='tarts'),
]
