from django.shortcuts import render, redirect, get_object_or_404
from .models import Pastry
from django.contrib import messages

def category_view(request, category):
    #Display pastry based on category
    category = category.upper()
    pastries = Pastry.objects.filter(
        pastry_category=category,
        is_available=True,
        is_custom=False
    )

    if not pastries.exists():
        messages.info(request, f"No {category.lower()}s are currently available.")

    return render(request, 'pastry/category.html', {
        'category': category.capitalize(),
        'pastries': pastries
    })


def customize_pastry(request, category):
    #Creating a custom pastry
    category = category.upper()

    if request.method == 'POST':
        pastry = Pastry.objects.create(
            pastry_name=f"Custom {category}",
            pastry_category=category,
            pastry_price=request.POST.get('price', 0) or 0,
            flavour=request.POST.get('flavour') or '',
            filling=request.POST.get('filling') or '',
            frosting=request.POST.get('frosting') or '',
            decoration=request.POST.get('decoration') or '',
            message=request.POST.get('message') or '',
            size=request.POST.get('size') or '',
            is_custom=True
        )

        #messages.success(request, f"Your custom {category.lower()} has been added to cart!")
        #return redirect('pastry:add_to_cart', pastry_id=pastry.id)

    # display form form custom cake
    return render(request, 'pastry/customize_pastry.html', {'category': category})
