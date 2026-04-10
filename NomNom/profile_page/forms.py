from django import forms
from login.models import User

from common.location import load_cities


class EditProfileForm(forms.ModelForm):
    CITY_CHOICES = [(city, city) for city in load_cities()]

    region = forms.ChoiceField(
        choices=[("", "Select region")] + CITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "gender",
            "region",
            "street",
            "profile_pic",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "profile_pic": forms.FileInput(attrs={"class": "form-control"}),
        }

    # Rely on User.save() to keep full_name in sync
