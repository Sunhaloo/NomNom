from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Pastry,
    CakeCustomisation,
    BrownieCustomisation,
    CookieCustomisation,
    CupcakeCustomisation,
    DoughnutCustomisation,
    TartCustomisation
)
from django.contrib import messages


def category_view(request, category):
    """
    Display all available pastries in a specific category.
    """
    category = category.upper()
    pastries = Pastry.objects.filter(pastry_category=category, is_available=True)

    if not pastries.exists():
        messages.info(request, f"No {category.lower()}s are currently available.")

    context = {
        'category': category.capitalize(),
        'pastries': pastries
    }

    return render(request, 'category.html', context)


def add_to_cart(request, pastry_id):
    """
    Add a selected pastry to the session cart.
    """
    pastry = get_object_or_404(Pastry, id=pastry_id)

    # Retrieve or create cart
    cart = request.session.get('cart', [])

    # Add the selected pastry to cart
    cart.append({
        'id': pastry.id,
        'name': pastry.pastry_name,
        'category': pastry.pastry_category,
        'price': float(pastry.pastry_price),
    })

    # Save cart back to session
    request.session['cart'] = cart
    messages.success(request, f"{pastry.pastry_name} added to cart!")

    return redirect('pastry:category_view', category=pastry.pastry_category.lower())


def customize_pastry(request, pastry_id):
    """
    Redirects to the correct customisation page based on pastry category.
    """
    pastry = get_object_or_404(Pastry, id=pastry_id)
    category = pastry.pastry_category

    # Redirect to the right customisation route
    if category == 'CAKE':
        return redirect('pastry:customize_cake', pastry_id=pastry.id)
    elif category == 'BROWNIE':
        return redirect('pastry:customize_brownie', pastry_id=pastry.id)
    elif category == 'COOKIE':
        return redirect('pastry:customize_cookie', pastry_id=pastry.id)
    elif category == 'CUPCAKE':
        return redirect('pastry:customize_cupcake', pastry_id=pastry.id)
    elif category == 'DOUGHNUT':
        return redirect('pastry:customize_doughnut', pastry_id=pastry.id)
    elif category == 'TART':
        return redirect('pastry:customize_tart', pastry_id=pastry.id)
    else:
        messages.warning(request, "This item cannot be customized.")
        return redirect('pastry:category_view', category=category.lower())
