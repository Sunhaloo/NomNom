from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from pastry.models import Pastry
from .models import Cart, CartItem
import json


@require_POST
def add_to_cart_ajax(request):
    """AJAX endpoint for adding items to cart"""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"}, status=401
        )

    try:
        data = json.loads(request.body)

        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(user=request.user)

        quantity = int(data.get("quantity", 1))
        product_name = data.get("name")
        product_category = data.get("category")

        try:
            query_kwargs = {"pastry_name": product_name, "is_custom": False}
            if product_category:
                query_kwargs["pastry_category"] = product_category

            pastry = Pastry.objects.get(**query_kwargs)
        except Pastry.DoesNotExist:
            print(
                f"Product not found: name={product_name}, category={product_category}"
            )
            print(f"Query kwargs: {query_kwargs}")
            return JsonResponse(
                {"success": False, "message": "Product not found"}, status=404
            )
        except Pastry.MultipleObjectsReturned:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Multiple products found. Please specify category.",
                },
                status=400,
            )

        # Update or create cart item
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, pastry=pastry, defaults={"quantity": quantity}
        )

        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"{product_name} (x{quantity}) added to cart!",
                "cart_count": cart.total_items,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@require_POST
def update_cart_quantity(request):
    """AJAX endpoint for updating cart item quantity"""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Authentication required"}, status=401
        )

    try:
        data = json.loads(request.body)
        item_index = int(data.get("index"))
        new_quantity = int(data.get("quantity"))

        if new_quantity < 1:
            return JsonResponse(
                {"success": False, "message": "Quantity must be at least 1"}, status=400
            )

        # Get user's cart
        cart = Cart.objects.get(user=request.user)
        cart_items = list(cart.items.all())

        if 0 <= item_index < len(cart_items):
            cart_item = cart_items[item_index]
            cart_item.quantity = new_quantity
            cart_item.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Quantity updated",
                    "cart_count": cart.total_items,
                }
            )
        else:
            return JsonResponse(
                {"success": False, "message": "Invalid item index"}, status=400
            )

    except Cart.DoesNotExist:
        return JsonResponse({"success": False, "message": "Cart not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
def add_to_cart(request, pastry_id=None):
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Adding preset cakes to carts
    if pastry_id:
        pastry = Pastry.objects.get(id=pastry_id)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, pastry=pastry, defaults={"quantity": 1}
        )
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        # Adding a customized cake to cart
        # Create a new custom pastry instance
        custom_pastry = Pastry.objects.create(
            pastry_name="Custom Cake",
            pastry_category="CAKE",  # Default category
            pastry_price=float(request.POST.get("price", 0)),
            flavour=request.POST.get("flavour", ""),
            filling=request.POST.get("filling", ""),
            frosting=request.POST.get("frosting", ""),
            decoration=request.POST.get("decoration", ""),
            size=request.POST.get("size", ""),
            layers=int(request.POST.get("layers", 1)),
            cake_message=request.POST.get("cake_message", ""),
            pickup_date=request.POST.get("pickup_date", None),
            is_custom=True,
            is_available=True,
        )

        CartItem.objects.create(cart=cart, pastry=custom_pastry, quantity=1)

    messages.success(request, "Item added to cart!")
    return redirect("cart:cart")


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related("pastry")

    # Calculate total
    total = cart.total_price

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

    return render(
        request,
        "cart/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "cart_json": cart_json,
            "total": total,
        },
    )


@login_required
def remove_from_cart(request, index):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = list(cart.items.all())

    if 0 <= index < len(items):
        item_to_remove = items[index]
        item_to_remove.delete()

    return redirect("cart:cart")


def clear_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
    messages.warning(request, "Your cart has been cleared.")
    return redirect("cart:cart")
