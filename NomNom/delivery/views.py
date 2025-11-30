from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Delivery

# Helper for staff-only access
def is_staff_user(user):
    return user.is_staff or user.is_superuser


@login_required
def delivery_list(request):
    """
    Show all deliveries.
    - Staff sees all deliveries.
    - Customers see only their own.
    """
    if request.user.is_staff:
        deliveries = Delivery.objects.select_related('order').order_by('-date')
    else:
        deliveries = Delivery.objects.filter(order__customer=request.user).select_related('order').order_by('-date')

    return render(request, 'delivery/delivery_list.html', {'deliveries': deliveries})


@login_required
def delivery_detail(request, delivery_id):
    """
    Show delivery details for a given delivery.
    Restrict to staff or the delivery’s order owner.
    """
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if not request.user.is_staff and delivery.order.customer != request.user:
        messages.error(request, "You do not have permission to view this delivery.")
        return redirect('delivery:delivery_list')

    return render(request, 'delivery/delivery_detail.html', {'delivery': delivery})


@user_passes_test(is_staff_user)
def update_delivery_status(request, delivery_id):
    """
    Allow staff to update a delivery’s status.
    """
    delivery = get_object_or_404(Delivery, id=delivery_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Done', 'Failed']:
            delivery.status = new_status
            delivery.save()
            messages.success(request, f"Delivery #{delivery.id} status updated to {new_status}.")
            return redirect('delivery:delivery_detail', delivery_id=delivery.id)
        else:
            messages.error(request, "Invalid status value.")

    return render(request, 'delivery/update_status.html', {'delivery': delivery})