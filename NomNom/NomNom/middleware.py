from __future__ import annotations

from django.conf import settings


class StaticMediaCorsMiddleware:
    """
    Add permissive CORS headers for static/media responses in development.

    This helps the Flet web app (served on a different localhost port) load
    images from Django's `/static/` and `/media/` URLs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not settings.DEBUG:
            return response

        path = request.path or ""
        static_url = getattr(settings, "STATIC_URL", "/static/") or "/static/"
        media_url = getattr(settings, "MEDIA_URL", "/media/") or "/media/"

        if path.startswith(static_url) or path.startswith(media_url):
            # Allow any origin to read image bytes in dev.
            response.headers.setdefault("Access-Control-Allow-Origin", "*")
            response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")

        return response

