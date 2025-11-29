from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pastry


"""View pastry by category, each of them will have preset values for their variables"""


def category_view(request, category):
    category_upper = category.upper()
    db_category = category_upper[:-1] if category_upper.endswith("S") else category_upper
    category_display = category.capitalize() + " Menu"

    # fetch pastries dynamically
    products = Pastry.objects.filter(
        pastry_category=db_category,
        is_available=True,
        is_custom=False
    )

    context = {
        "category_name": category_display,
        "products": products,
        "db_category": db_category,
    }
    return render(request, "pastry/category.html", context)


"""View a customisable cake - only category has been preset(as only cakes should be customisable)"""


def customize_pastry(request):
    """
    Displays the cake customization form (GET)
    and saves a custom cake (POST).
    """
    category = "CAKE"

    if request.method == "POST":
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to create a custom cake!")
            return redirect("login:login")

        # Validate pickup date
        pickup_date_str = request.POST.get("pickup_date", "")
        if pickup_date_str:
            try:
                from datetime import datetime, date

                pickup_date = datetime.strptime(pickup_date_str, "%Y-%m-%d").date()

                # Check if date is in the future
                if pickup_date < date.today():
                    messages.error(request, "Pickup date must be in the future!")
                    return redirect("pastry:customize")
            except ValueError:
                messages.error(request, "Invalid date format!")
                return redirect("pastry:customize")
        else:
            pickup_date = None

        # Create a new custom cake from form input
        pastry = Pastry.objects.create(
            pastry_name="Custom Cake",
            pastry_category=category,
            pastry_price=request.POST.get("price", 0),
            flavour=request.POST.get("flavour", ""),
            filling=request.POST.get("filling", ""),
            frosting=request.POST.get("frosting", ""),
            decoration=request.POST.get("decoration", ""),
            size=request.POST.get("size", ""),
            layers=int(request.POST.get("layers", 1)),
            cake_message=request.POST.get("cake_message", ""),
            pickup_date=pickup_date,
            is_custom=True,
            is_available=True,
        )
        # Add the custom cake to the cart directly from this view
        cart = request.session.get("cart", [])
        cart.append(
            {
                "name": "Custom Cake",
                "price": float(pastry.pastry_price),
                "flavour": pastry.flavour,
                "filling": pastry.filling,
                "frosting": pastry.frosting,
                "decoration": pastry.decoration,
                "size": pastry.size,
                "is_custom": True,
            }
        )
        request.session["cart"] = cart
        messages.success(request, "Your custom cake has been added to cart!")
        # Add to cart
        from cart.models import Cart, CartItem

        cart, created = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.create(cart=cart, pastry=pastry, quantity=1)

    # Render the customization form page
    return render(request, "pastry/customize_pastry.html", {"category": category})


def login_required_gate(request):
    """Display login gate page for non-authenticated users trying to add to cart"""
    return render(request, "pastry/login_required.html")
