from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    # return HttpResponse("Hello World From Login")
    return render(request, "login/login.html")


def signup(request):
    # return HttpResponse("Hello World From Login")
    return render(request, "login/signup.html")
