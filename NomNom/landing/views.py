from django.http import HttpResponse
from django.shortcuts import render


from pastry.models import Pastry

def index(request):
    try:
        fudgy_cake = Pastry.objects.get(pastry_name='Fudgy McFudgecake')
    except Pastry.DoesNotExist:
        fudgy_cake = None
        
    return render(request, "landing/landing.html", {'fudgy_cake': fudgy_cake})
