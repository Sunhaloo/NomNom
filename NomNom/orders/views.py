from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from cart.models import Cart, CartItem
from .models import Order, OrderDetail

@login_required
def checkout(request):
    """Display checkout form and create an Order when user confirms."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart')

    # Prepare cart data for JavaScript
    import json
    cart_data = []
    for item in cart_items:
        if item.pastry.image:
            if item.pastry.is_custom and hasattr(item.pastry.image, "url"):
                image_path = item.pastry.image.url
            else:
                image_path = str(item.pastry.image)
        else:
            image_path = ""

        # Format name with category (e.g., "Vanilla Tart" instead of just "Vanilla")
        category_name = item.pastry.pastry_category.title()
        if category_name.endswith("S"):
            # Remove plural 's' (e.g., "CAKES" -> "Cake")
            category_name = category_name[:-1]

        if item.pastry.is_custom:
            display_name = item.pastry.pastry_name
        else:
            display_name = f"{item.pastry.pastry_name} {category_name}"

        cart_data.append(
            {
                "name": display_name,
                "price": float(item.pastry.pastry_price),
                "quantity": item.quantity,
                "image": image_path,
                "is_custom": item.pastry.is_custom,
                "flavour": item.pastry.flavour,
                "filling": item.pastry.filling,
                "frosting": item.pastry.frosting,
                "decoration": item.pastry.decoration,
                "size": item.pastry.size,
                "layers": item.pastry.layers,
                "cake_message": item.pastry.cake_message,
                "pickup_date": (
                    str(item.pastry.pickup_date) if item.pastry.pickup_date else None
                ),
            }
        )

    cart_json = json.dumps(cart_data)

    if request.method == 'POST':
        # Create the order record
        order = Order.objects.create(
            customer=request.user,
            order_date=timezone.now(),
            total_amount=cart.total_price,
            order_status="Pending",
            is_preorder=False
        )

        # Create related order details
        for item in cart_items:
            OrderDetail.objects.create(
                order=order,
                pastry=item.pastry,
                price=item.pastry.pastry_price,
                quantity=item.quantity
            )

        # Clear cart after checkout
        cart.items.all().delete()

        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('payment:payment_page', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_json': cart_json,
        'total': cart.total_price
    })

