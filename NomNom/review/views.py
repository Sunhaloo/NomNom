from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from pastry.models import Pastry
from orders.models import OrderDetail
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
    user = request.user

    try:
        # Check if the user has ordered this pastry before (any order status)
        has_ordered = OrderDetail.objects.filter(
            order__user=user,
            pastry=pastry
        ).exists()

        if not has_ordered:
            return JsonResponse({
                "success": False,
                "error": "You can only review pastries you have ordered."
            }, status=400)

        # Check if the user has already reviewed this pastry - double check before transaction
        if Review.objects.filter(user=user, pastry=pastry).exists():
            return JsonResponse({
                "success": False,
                "error": "You've already reviewed this pastry."
            }, status=400)

        with transaction.atomic():
            # Check again inside transaction for race conditions
            existing_review = Review.objects.select_for_update().filter(
                user=user,
                pastry=pastry
            ).exists()

            if existing_review:
                return JsonResponse({
                    "success": False,
                    "error": "You've already reviewed this pastry."
                }, status=400)

            data = json.loads(request.body)
            rating = int(data.get("rating", 0))
            comment = data.get("comment", "").strip()

            if not (1 <= rating <= 5):
                return JsonResponse({"success": False, "error": "Invalid rating value."}, status=400)
            if not comment:
                return JsonResponse({"success": False, "error": "Comment cannot be empty."}, status=400)

            review = Review.objects.create(
                user=user,
                pastry=pastry,
                rating=rating,
                comment=comment,
                date=timezone.now(),
            )

            # Verify the review was created and is unique
            if Review.objects.filter(user=user, pastry=pastry).count() > 1:
                # This should never happen due to the checks, but just in case
                review.delete()
                return JsonResponse({
                    "success": False,
                    "error": "Duplicate review detected. Please try again."
                }, status=400)

            return JsonResponse({"success": True, "message": "Review submitted successfully!"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)