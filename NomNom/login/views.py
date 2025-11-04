from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .forms import SignupForm

User = get_user_model()


# Create your views here.
def index(request):
    # return HttpResponse("Hello World From Login")
    return render(request, "login/login.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data.get("password1")
            )  # Use password1 from form
            user.save()
            return redirect("login:login")
    else:
        form = SignupForm()

    return render(request, "login/signup.html", {"form": form})
