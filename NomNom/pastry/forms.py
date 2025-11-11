from django import forms
from .models import (
    CakeCustomisation,
    BrownieCustomisation,
    CookieCustomisation,
    CupcakeCustomisation,
    DoughnutCustomisation,
    TartCustomisation
)

# Each form connects to its corresponding model
class CakeCustomisationForm(forms.ModelForm):
    class Meta:
        model = CakeCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']

class BrownieCustomisationForm(forms.ModelForm):
    class Meta:
        model = BrownieCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']

class CookieCustomisationForm(forms.ModelForm):
    class Meta:
        model = CookieCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']

class CupcakeCustomisationForm(forms.ModelForm):
    class Meta:
        model = CupcakeCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']

class DoughnutCustomisationForm(forms.ModelForm):
    class Meta:
        model = DoughnutCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']

class TartCustomisationForm(forms.ModelForm):
    class Meta:
        model = TartCustomisation
        fields = '__all__'
        exclude = ['category', 'is_custom', 'is_available']
