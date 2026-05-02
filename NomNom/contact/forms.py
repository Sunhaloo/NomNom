from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "message"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "id": "first-name",
                    "name": "first-name",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "id": "last-name",
                    "name": "last-name",
                    "placeholder": "Last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "id": "email",
                    "name": "email",
                    "placeholder": "you@example.com",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "id": "message",
                    "name": "message",
                    "rows": 4,
                    "placeholder": "How can we help?",
                }
            ),
        }

    def clean_email(self):
        """Apply a slightly stricter email rule than the default.

        Django's EmailField is quite permissive; for this contact form we
        want to only accept "reasonable" addresses like user@example.com.
        """
        email = (self.cleaned_data.get("email") or "").strip()

        # Basic pattern: simple local-part and a domain with at least one dot
        # and a final TLD of 2-4 letters (e.g. .com, .mu, .co.uk → 'uk').
        import re

        pattern = re.compile(r"^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$")
        if not pattern.match(email):
            raise forms.ValidationError("Please enter a valid email address.")

        return email
