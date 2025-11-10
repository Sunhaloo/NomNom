from django.shortcuts import render
from .models import Pastry

def cakes(request):
    pastries = Pastry.objects.filter(category='CAKE')
    return render(request, 'pastry/category.html', {'category': 'Cakes', 'pastries': pastries})

def brownies(request):
    pastries = Pastry.objects.filter(category='BROWNIE')
    return render(request, 'pastry/category.html', {'category': 'Brownies', 'pastries': pastries})

def cupcakes(request):
    pastries = Pastry.objects.filter(category='CUPCAKE')
    return render(request, 'pastry/category.html', {'category': 'Cupcakes', 'pastries': pastries})

def cookies(request):
    pastries = Pastry.objects.filter(category='COOKIE')
    return render(request, 'pastry/category.html', {'category': 'Cookies', 'pastries': pastries})

def doughnuts(request):
    pastries = Pastry.objects.filter(category='DOUGHNUT')
    return render(request, 'pastry/category.html', {'category': 'Doughnut', 'pastries': pastries})

def tarts(request):
    pastries = Pastry.objects.filter(category='TART')
    return render(request, 'pastry/category.html', {'category': 'Tarts', 'pastries': pastries})

