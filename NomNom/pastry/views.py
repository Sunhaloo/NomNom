from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pastry


'''View pastry by category, each of them will have preset values for their variables'''
def category_view(request, category):
    category_upper = category.upper()
    products = []
    category_display = category.capitalize() + " Menu"
    product_template = 'pastry/includes/product_card.html'

    if category_upper == 'CAKES':
        products = [
            {
                'name': 'Vanilla',
                'price': '1000',
                'rating': 0,
                'reviews': 0,
                'image': 'images/vanilla_cake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Cheesecake',
                'price': '750',
                'rating': 0,
                'reviews': 0,
                'image': 'images/cheese_cake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Mint',
                'price': '500',
                'rating': 0,
                'reviews': 0,
                'image': 'images/mint_cake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Chocolate',
                'price': '1750',
                'rating': 0,
                'reviews': 0,
                'image': 'images/chocolate_cake.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]
    elif category_upper == 'BROWNIES':
        products = [
            {
                'name': 'Strawberry',
                'price': '500',
                'rating': 0,
                'reviews': 0,
                'image': 'images/strawberry_brownie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Chocolate',
                'price': '750',
                'rating': 0,
                'reviews': 0,
                'image': 'images/chocolate_brownie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Rasberry',
                'price': '850',
                'rating': 0,
                'reviews': 0,
                'image': 'images/rasberry_brownie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Vanilla',
                'price': '600',
                'rating': 0,
                'reviews': 0,
                'image': 'images/vanilla_brownie.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]
    elif category_upper == 'CUPCAKES':
        products = [
            {
                'name': 'Rasberry',
                'price': '450',
                'rating': 0,
                'reviews': 0,
                'image': 'images/rasberry_cupcake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Chocolate',
                'price': '900',
                'rating': 0,
                'reviews': 0,
                'image': 'images/chocolate_cupcake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Oreo',
                'price': '500',
                'rating': 0,
                'reviews': 0,
                'image': 'images/oreo_cupcake.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Strawberry',
                'price': '600',
                'rating': 0,
                'reviews': 0,
                'image': 'images/strawberry_cupcake.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]
    elif category_upper == 'COOKIES':
        products = [
            {
                'name': 'Chocolate Chip',
                'price': '450',
                'rating': 0,
                'reviews': 0,
                'image': 'images/chocolatechip_cookie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Oat',
                'price': '400',
                'rating': 0,
                'reviews': 0,
                'image': 'images/oat_cookie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Fruit',
                'price': '500',
                'rating': 0,
                'reviews': 0,
                'image': 'images/fruit_cookie.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Smarties',
                'price': '425',
                'rating': 0,
                'reviews': 0,
                'image': 'images/smarties_cookie.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]
    elif category_upper == 'DONUTS':
        db_category = 'DONUT'
        products = [
            {
                'name': 'Strawberry',
                'price': '400',
                'rating': 0,
                'reviews': 0,
                'image': 'images/strawberry_donut.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Chocolate',
                'price': '450',
                'rating': 0,
                'reviews': 0,
                'image': 'images/chocolate_donut.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Vanilla',
                'price': '425',
                'rating': 0,
                'reviews': 0,
                'image': 'images/vanilla_donut.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Cinnamon Sugar',
                'price': '350',
                'rating': 0,
                'reviews': 0,
                'image': 'images/cinnamonsugar_donut.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]
    elif category_upper == 'TARTS':
        products = [
            {
                'name': 'Cranberry',
                'price': '450',
                'rating': 0,
                'reviews': 0,
                'image': 'images/cranberry_tart.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Vanilla',
                'price': '375',
                'rating': 0,
                'reviews': 0,
                'image': 'images/vanilla_tart.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Red Fruits',
                'price': '400',
                'rating': 0,
                'reviews': 0,
                'image': 'images/redfruit_tart.png',
                'stars': [0, 0, 0, 0, 0]
            },
            {
                'name': 'Banana',
                'price': '350',
                'rating': 0,
                'reviews': 0,
                'image': 'images/banana_tart.png',
                'stars': [0, 0, 0, 0, 0]
            }
        ]

    db_category = category_upper[:-1] if category_upper.endswith('S') else category_upper
    
    context = {
        'category_name': category_display,
        'products': products,
        'product_template': product_template,
        'db_category': db_category
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
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to create a custom cake!")
            return redirect('login:login')
        
        # Validate pickup date
        pickup_date_str = request.POST.get('pickup_date', '')
        if pickup_date_str:
            try:
                from datetime import datetime, date
                pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
                
                # Check if date is in the future
                if pickup_date < date.today():
                    messages.error(request, "Pickup date must be in the future!")
                    return redirect('pastry:customize')
            except ValueError:
                messages.error(request, "Invalid date format!")
                return redirect('pastry:customize')
        else:
            pickup_date = None
        
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
            layers=int(request.POST.get('layers', 1)),
            cake_message=request.POST.get('cake_message', ''),
            pickup_date=pickup_date,
            is_custom=True,
            is_available=True
        )
        
        # Add to cart
        from cart.models import Cart, CartItem
        cart, created = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.create(
            cart=cart,
            pastry=pastry,
            quantity=1
        )
        
        return redirect('cart:cart')

    # Render the customization form page
    return render(request, 'pastry/customize_pastry.html', {'category': category})


def login_required_gate(request):
    """Display login gate page for non-authenticated users trying to add to cart"""
    return render(request, 'pastry/login_required.html')
