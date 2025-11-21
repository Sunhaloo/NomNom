from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pastry


'''View pastry by category, each of them will have preset values for their variables'''
def category_view(request, category):
    category = category.upper()
    try:
        pastries = Pastry.objects.filter(
            pastry_category=category,
            is_available=True,
            is_custom=False
        ).order_by('pastry_name')
    except Exception as e:
        # Handle unexpected database errors
        pastries = []
        # Log the error for debugging purposes
        print(f"Database error in category_view: {e}")

    context = {
        'category': category.capitalize(),
        'pastries': pastries
    }
    return render(request, 'pastry/category.html', context)


'''View a customisable cake - only category has been preset(as only cakes should be customisable)'''
def customize_pastry(request):
    """
    Displays the cake customization form (GET)
    and saves a custom cake (POST).
    """
    category = "CAKE" 

    if request.method == 'POST':
        # Create a new custom cake from form input
        pastry = Pastry.objects.create(
            pastry_name="Custom Cake",
            pastry_category=category,
            pastry_price=request.POST.get('price', 0),
            flavour=request.POST.get('flavour', ''),
            filling=request.POST.get('filling', ''),
            frosting=request.POST.get('frosting', ''),
            decoration=request.POST.get('decoration', ''),
            size=request.POST.get('size', ''),
            is_custom=True
        )

        # Add the custom cake to the cart directly from this view
        cart = request.session.get('cart', [])
        cart.append({
            'name': 'Custom Cake',
            'price': float(pastry.pastry_price),
            'flavour': pastry.flavour,
            'filling': pastry.filling,
            'frosting': pastry.frosting,
            'decoration': pastry.decoration,
            'size': pastry.size,
            'is_custom': True
        })
        request.session['cart'] = cart
        messages.success(request, "Your custom cake has been added to cart!")
        return redirect('cart:cart')

    # Render the customization form page
    return render(request, 'pastry/customize_pastry.html', {'category': category})


