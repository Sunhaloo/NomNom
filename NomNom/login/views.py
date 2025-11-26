from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .forms import SignupForm, LoginForm, PasswordResetForm

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


def forget_passwd(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.filter(email=email).first()
            except Exception as e:
                # Handle unexpected database errors
                print(f"Database error in password reset: {e}")
                messages.error(request, "An error occurred. Please try again later.")
                return render(request, "login/forget_passwd.html", {"form": form})

            if user:
                try:
                    # Generate password reset token and URL
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))

                    # Get the current site for the password reset link
                    current_site = get_current_site(request)

                    # Create the password reset email
                    subject = "Password Reset Request"
                    message = render_to_string(
                        "login/password_reset_email.html",
                        {
                            "user": user,
                            "domain": current_site.domain,
                            "uid": uid,
                            "token": token,
                        },
                    )

                    # send the email
                    send_mail(
                        subject,
                        message,
                        None,  # Use the DEFAULT_FROM_EMAIL setting
                        [email],
                        fail_silently=False,
                    )
                except Exception as e:
                    # Handle email sending errors
                    print(f"Email sending error: {e}")
                    messages.error(request, "Failed to send password reset email.")
                    return render(request, "login/forget_passwd.html", {"form": form})

                # redirect to a success page or display a message
                return render(request, "login/password_reset_sent.html")
            else:
                # if email doesn't exist, still show success to prevent email enumeration
                return render(request, "login/password_reset_sent.html")
    else:
        form = PasswordResetForm()

    return render(request, "login/forget_passwd.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Valid token, show password reset form
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password and new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect("login:login")
            else:
                return render(
                    request,
                    "login/password_reset_form.html",
                    {"validlink": True, "error": "Passwords do not match"},
                )

        return render(request, "login/password_reset_form.html", {"validlink": True})
    else:
        # Invalid token
        return render(request, "login/password_reset_form.html", {"validlink": False})


def logout_view(request):
    logout(request)
    return redirect("landing:landing")
