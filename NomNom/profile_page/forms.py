from django import forms
from login.models import User

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "username", "gender", "region", "street", "profile_pic"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "region": forms.TextInput(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),
        }
