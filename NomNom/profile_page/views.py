from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditProfileForm

# Create your views here.
@login_required
def profile_view(request):
    # profile page just needs request.user in template
    return render(request, "profile_page/profile.html")

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile_page:profile")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EditProfileForm(instance=user)

    return render(request, "profile_page/edit_profile.html", {"form": form})

@login_required
def clear_profile_pic(request):
    user = request.user
    # Safely delete file only if present
    if user.profile_pic:
        try:
            user.profile_pic.delete(save=False)
        except Exception:
            # ignore deletion errors (file might be missing)
            pass
    user.profile_pic = None
    user.save()
    messages.success(request, "Profile picture cleared.")
    return redirect("profile_page:profile")