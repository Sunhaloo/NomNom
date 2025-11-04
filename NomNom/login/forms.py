from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "auth-input", "placeholder": "Email"}),
    )
    gender = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female")],
        widget=forms.Select(attrs={"class": "auth-input"}),
    )
    first_name = forms.CharField(
        max_length=80,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "placeholder": "Last Name"}
        ),
    )
    region = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Region"}),
    )
    street = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Street"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "gender",
            "region",
            "street",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "auth-input", "placeholder": "Confirm Password"}
        )
