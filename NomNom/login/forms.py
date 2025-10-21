from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[("M", "Male"), ("F", "Female")])
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=120)
    region = forms.CharField(max_length=80)
    street = forms.CharField(max_length=120)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "firstName",
            "lastName",
            "gender",
            "region",
            "street",
        ]
