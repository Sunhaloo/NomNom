from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
from .forms import EditProfileForm

# Create your views here.
@login_required
def profile_view(request):
    user = request.user

    has_profile_pic = False
    profile_pic_url = static("images/default_profile.png")

    if user.profile_pic and getattr(user.profile_pic, "name", ""):
        try:
            if user.profile_pic.storage.exists(user.profile_pic.name):
                has_profile_pic = True
                profile_pic_url = user.profile_pic.url
        except Exception:
            # Treat any storage error as "missing" and fall back to default.
            pass

    return render(
        request,
        "profile_page/profile.html",
        {"profile_pic_url": profile_pic_url, "has_profile_pic": has_profile_pic},
    )

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
