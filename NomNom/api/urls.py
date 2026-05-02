from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserView,
    CustomTokenView,
    DeliveryViewSet,
    LogoutView,
    OrderViewSet,
    BusinessStatsView,
    TopReviewsView,
    SignupView,
    PastryBannerView,
)

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"deliveries", DeliveryViewSet, basename="delivery")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", CustomTokenView.as_view(), name="api-token-auth"),
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("auth/signup/", SignupView.as_view(), name="api-signup"),
    path("stats/", BusinessStatsView.as_view(), name="business-stats"),
    path("reviews/top-rated/", TopReviewsView.as_view(), name="top-reviews"),
    path("pastries/banner/", PastryBannerView.as_view(), name="pastry-banner"),
]
