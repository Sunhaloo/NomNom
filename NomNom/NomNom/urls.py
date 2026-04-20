from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

#from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # WARNING: the order of "operations" matter
    path("", include("landing.urls")),
    path("about_us/", include("about_us.urls")),
    path("login/", include("login.urls")),
    path("contact/", include("contact.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls")),
    path("review/", include("review.urls")),
    path("admin/", admin.site.urls),
    path("pastry/", include("pastry.urls")),
    path("profile/", include("profile_page.urls")),
    path("api/v1/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
