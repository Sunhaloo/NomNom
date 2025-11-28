from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from orders.models import Order
from .models import Payment

@login_required
def payment_page(request, order_id):
    """Render the payment page for a specific order."""
    order = get_object_or_404(Order, id=order_id)

    # Calculate amount dynamically if not yet set
    amount_due = order.total_amount if hasattr(order, 'total_amount') else 0.00

    context = {
        'order': order,
        'amount': amount_due,
    }
    return render(request, 'payment/payment.html', context)


@login_required
def process_payment(request, order_id):
    """Handle payment submission (mocked for now)."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'Card')

        # Create a payment record
        payment = Payment.objects.create(
            order=order,
            payment_method=method,
            amount=order.total_amount,
            payment_status="Paid",
            payment_date=timezone.now()
        )

        # Update order status
        order.order_status = "Paid"
        order.save()

        messages.success(request, f"Payment successful for Order #{order.id}!")
        return redirect('orders:checkout')  # You can later change this to delivery or order summary

    # If somehow accessed via GET, redirect back to payment page
    return redirect('payment:payment_page', order_id=order_id)
