from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from pastry.models import Pastry
from .models import Review
import json


def get_reviews(request, pastry_id):
    """Return all reviews for a given pastry as JSON."""
    pastry = get_object_or_404(Pastry, id=pastry_id)
    reviews = Review.objects.filter(pastry=pastry).select_related('user').order_by('-date')

    data = [
        {
            "user": review.user.username,
            "rating": review.rating,
            "comment": review.comment,
            "date": review.date.strftime("%b %d, %Y"),
        }
        for review in reviews
    ]
    return JsonResponse({"reviews": data}, status=200)


@login_required
@require_POST
def add_review(request, pastry_id):
    """Save a new review from modal form (AJAX)."""
    pastry = get_object_or_404(Pastry, id=pastry_id)

    try:
        data = json.loads(request.body)
        rating = int(data.get("rating"))
        comment = data.get("comment", "").strip()

        if not (1 <= rating <= 5):
            return JsonResponse({"success": False, "error": "Invalid rating value."}, status=400)
        if not comment:
            return JsonResponse({"success": False, "error": "Comment cannot be empty."}, status=400)

        Review.objects.create(
            user=request.user,
            pastry=pastry,
            rating=rating,
            comment=comment,
            date=timezone.now(),
        )

        return JsonResponse({"success": True, "message": "Review submitted successfully!"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)