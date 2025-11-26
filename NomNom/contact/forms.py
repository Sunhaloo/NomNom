from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input', 
                'id': 'first-name', 
                'name': 'first-name', 
                'placeholder': 'Aisha'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input', 
                'id': 'last-name', 
                'name': 'last-name', 
                'placeholder': 'Ramjahn'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 
                'id': 'email', 
                'name': 'email', 
                'placeholder': 'aisha@gmail.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input', 
                'id': 'message', 
                'name': 'message', 
                'rows': 4, 
                'placeholder': 'Enter your question or message'
            }),
        }