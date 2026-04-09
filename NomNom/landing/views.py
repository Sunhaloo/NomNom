from django.shortcuts import render
from pastry.models import Pastry


def index(request):
    try:
        fudgy_cake = Pastry.objects.get(pastry_name="Fudgy McFudgecake")
    except Pastry.DoesNotExist:
        fudgy_cake = None

    order_success = request.GET.get("order_success") == "1"
    order_id = request.GET.get("order_id")

    return render(
        request,
        "landing/landing.html",
        {
            "fudgy_cake": fudgy_cake,
            "order_success": order_success,
            "order_id": order_id,
        },
    )
