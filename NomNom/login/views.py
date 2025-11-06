from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from .forms import SignupForm, LoginForm

User = get_user_model()


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("landing:landing")
    else:
        form = LoginForm()
    return render(request, "login/login.html", {"form": form})


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("landing:landing")
    else:
        form = SignupForm()

    return render(request, "login/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("landing:landing")
