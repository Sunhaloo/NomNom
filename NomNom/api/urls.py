from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, DeliveryViewSet


router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"deliveries", DeliveryViewSet, basename="delivery")


urlpatterns = [
    path("", include(router.urls)),
]
