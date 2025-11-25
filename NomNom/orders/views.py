from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from cart.models import Cart
from .models import Order, OrderDetail

from pathlib import Path
import json

def format_pastry_name(item):
    pastry = item.pastry
    category = pastry.pastry_category.title()

    # remove final 'S' (Cakes → Cake)
    if category.endswith("S"):
        category = category[:-1]

    if pastry.is_custom:
        return pastry.pastry_name

    return f"{pastry.pastry_name} {category}"


def resolve_image(item):
    pastry = item.pastry

    if not pastry.image:
        return ""

    # Custom pastries require `.url`, normal ones output string
    if pastry.is_custom and hasattr(pastry.image, "url"):
        return pastry.image.url

    return str(pastry.image)


def serialize_cart_items(cart_items):
    data = []

    for item in cart_items:
        data.append({
            "name": format_pastry_name(item),
            "price": float(item.pastry.pastry_price),
            "quantity": item.quantity,
            "image": resolve_image(item),

            # Extra fields for custom cakes
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
        })

    return data

# Load cities.json

def load_cities():
    cities_path = Path(settings.BASE_DIR) / "orders/static/orders/cities.json"
    if cities_path.exists():
        with open(cities_path, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                return content.get("cities", [])
            except Exception:
                return []
    return []


#  Checkout Page
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart')

    # Convert cart into JSON-friendly objects
    cart_data = serialize_cart_items(cart_items)
    cart_json = json.dumps(cart_data)

    # Load cities from JSON file
    cities = load_cities()

    # Handle form POST → create the order
    if request.method == "POST":
        order = Order.objects.create(
            customer=request.user,
            order_date=timezone.now(),
            total_amount=cart.total_price,
            order_status="Pending",
            is_preorder=False
        )

        # Create order line items
        for item in cart_items:
            OrderDetail.objects.create(
                order=order,
                pastry=item.pastry,
                price=item.pastry.pastry_price,
                quantity=item.quantity
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('payment:payment_page', order_id=order.id)

    # Render template
    return render(request, 'orders/checkout.html', {
        "cart": cart,
        "cart_items": cart_items,
        "cart_json": cart_json,
        "total": cart.total_price,
        "cities": cities,
    })