from django.contrib.auth.decorators import login_required    #ensure that only logged in customers can add to cart/view their cart
from django.shortcuts import render, redirect
from django.contrib import messages
from pastry.models import Pastry

@login_required #using decorator authentication to ensure login user can add to cart
def add_to_cart(request, pastry_id=None):
    cart = request.session.get('cart', [])

    # Adding preset cakes to carts
    if pastry_id:
        try:
            pastry = Pastry.objects.get(id=pastry_id)
            cart.append({
                'pastry_id': pastry.id,
                'name': pastry.pastry_name,
                'price': float(pastry.pastry_price),
                'quantity': 1,
                'is_custom': False,
            })
        except Pastry.DoesNotExist:
            messages.error(request, "The selected pastry does not exist.")
            return redirect('pastry:category_view', category='cake')  # Redirect to pastry page
    else:
        # Adding a customized cake to cart
        cart.append({
            'name': 'Custom Cake',
            'price': float(request.POST.get('price', 0)),
            'flavour': request.POST.get('flavour', ''),
            'filling': request.POST.get('filling', ''),
            'frosting': request.POST.get('frosting', ''),
            'decoration': request.POST.get('decoration', ''),
            'size': request.POST.get('size', ''),
            'is_custom': True
        })

    request.session['cart'] = cart
    messages.success(request, "Item added to cart!")
    return redirect('cart:view_cart')

@login_required #using decorator authentication to ensure login user can view to cart
def view_cart(request):
    cart = request.session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render(request, 'cart/cart.html', {'cart': cart, 'total': total})

@login_required #using decorator authentication to ensure login user can remove an item from cart
def remove_from_cart(request, index):
    cart = request.session.get('cart', [])
    if 0 <= index < len(cart):
        try:
            cart.pop(index)
            request.session['cart'] = cart
            messages.info(request, "Item removed from cart.")
        except IndexError:
            messages.error(request, "Invalid item index.")
    else:
        messages.error(request, "Invalid item index.")
    return redirect('cart:view_cart')


def clear_cart(request):
    request.session['cart'] = []
    messages.warning(request, "Your cart has been cleared.")
    return redirect('cart:view_cart')

