from django.http import HttpResponse
from django.shortcuts import render


# our very first view
def index(request):
    # return HttpResponse("Hello World From Index Page")
    return render(request, "landing/landing.html")
