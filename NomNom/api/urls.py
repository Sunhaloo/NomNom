from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, DeliveryViewSet, LogoutView, OrderViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"deliveries", DeliveryViewSet, basename="delivery")


urlpatterns = [
    path("", include(router.urls)),
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
]
