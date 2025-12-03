from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from cart.models import Cart
from .models import Order, OrderDetail
from delivery.models import Delivery

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
            user=request.user,
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
        # Create delivery record from form data
        # Extract delivery information from form (this needs to come from the checkout form)
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        street_address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        zip_code = request.POST.get('zip', '').strip()
        country = request.POST.get('country', 'Mauritius').strip()

        # If form fields are empty, fallback to user profile information
        user = request.user
        if not first_name:
            first_name = user.first_name
        if not last_name:
            last_name = user.last_name
        if not street_address:
            street_address = getattr(user, 'street', '')
        if not city:
            city = getattr(user, 'region', '')

        # Build address with proper formatting, skipping empty parts
        address_parts = []
        if first_name or last_name:
            name_part = f"{first_name} {last_name}".strip()
            if name_part:
                address_parts.append(name_part)
        if street_address:
            address_parts.append(street_address)
        if city:
            address_parts.append(city)
        if zip_code:
            address_parts.append(zip_code)
        if country:
            address_parts.append(country)

        delivery_address = ", ".join(address_parts) if address_parts else f"{getattr(user, 'street', 'Address not specified')}, {getattr(user, 'region', 'Region not specified')}"

        # Determine delivery date (for now, assume next day for express delivery)
        from datetime import timedelta
        delivery_date = timezone.now().date() + timedelta(days=1)  # Default to tomorrow

        # Check if delivery date was provided in the form
        selected_date = request.POST.get('deliveryDate')
        if selected_date:
            try:
                from datetime import datetime
                delivery_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except ValueError:
                # If parsing fails, keep the default date
                pass

        Delivery.objects.create(
            order=order,
            address=delivery_address,
            date=delivery_date,
            status='Pending'  # Default status
        )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.id} created successfully!")
        return redirect('orders:order_confirmation', order_id=order.id)

    # Render template
    return render(request, 'orders/checkout.html', {
        "cart": cart,
        "cart_items": cart_items,
        "cart_json": cart_json,
        "total": cart.total_price,
        "cities": cities,
        "user_profile": request.user  # Pass user profile data to template
    })


# Order Confirmation View
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Get order details (pastries, quantity, price)
    order_details = order.order_details.all()

    # Get delivery information - get the latest delivery record for the order
    try:
        delivery = Delivery.objects.filter(order=order).latest('id')
    except Delivery.DoesNotExist:
        delivery = None

    context = {
        'order': order,
        'order_details': order_details,
        'delivery': delivery,
        'user_profile': request.user  # Include user profile for address fallback
    }

    return render(request, 'orders/order_confirmation.html', context)