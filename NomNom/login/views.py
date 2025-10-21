from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


# Create your views here.
def index(request):
    # return HttpResponse("Hello World From Login")
    return render(request, "login/login.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        gender = request.POST.get("gender")
        region = request.POST.get("region")
        street = request.POST.get("street")

        # basic validation
        if not all(
            [username, email, password, first_name, last_name, gender, region, street]
        ):
            return render(
                request, "login/signup.html", {"error": "Please fill in all fields."}
            )

        # check if username or email already exists
        if User.objects.filter(username=username).exists():
            return render(
                request, "login/signup.html", {"error": "Username already taken."}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request, "login/signup.html", {"error": "Email already registered."}
            )

        # create the new user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # securely hash password
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            region=region,
            street=street,
            role="CUSTOMER",
        )

        # redirect to login page after success
        return redirect("login:login")

    return render(request, "login/signup.html")
