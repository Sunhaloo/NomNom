from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import ContactForm


def index(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message
            contact_message = form.save()

            # Send confirmation email to the user
            try:
                subject = "NomNom Contact Message Received"
                message = render_to_string(
                    "contact/contact_confirmation_email.html",
                    {
                        "first_name": contact_message.first_name,
                        "last_name": contact_message.last_name,
                        "message": contact_message.message,
                        "created_at": contact_message.created_at
                    },
                )

                send_mail(
                    subject,
                    message,
                    None,  # Use DEFAULT_FROM_EMAIL setting
                    [contact_message.email],
                    fail_silently=False,
                )

                messages.success(request, "Your message has been sent successfully! A confirmation email has been sent to your address.")
                return redirect('contact:contact')  # Redirect to avoid resubmission
            except Exception as e:
                # If email sending fails, still save the message and show an error
                messages.error(request, f"Your message was sent but we couldn't send a confirmation email. Error: {str(e)}")
                return redirect('contact:contact')
    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form})
