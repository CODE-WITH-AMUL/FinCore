from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfileData, CompanyInformation


@login_required
def userprofile(request):
    user_profile, _ = UserProfileData.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.get_full_name()},
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        bio = request.POST.get("bio", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        user_profile.name = name
        user_profile.bio = bio

        if profile_picture:
            user_profile.profile_picture = profile_picture

        user_profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("userprofile")

    # Company: prefer the linked company on the profile; fall back to the
    # singleton CompanyInformation row if the FK is empty.
    company_info = getattr(user_profile, "company", None)
    if company_info is None:
        company_info = CompanyInformation.objects.first()

    context = {
        "user_profile": user_profile,
        "company_info": company_info,
        # optional extras the template expects:
        "user_role": getattr(user_profile, "role", None) or "Administrator",
        "account_status": "Active" if request.user.is_active else "Inactive",
        "email_verified": request.user.email.endswith("@") is False and bool(request.user.email),
        "member_since": request.user.date_joined.strftime("%b %d, %Y") if request.user.date_joined else "—",
        "last_login_display": request.user.last_login.strftime("%b %d, %Y · %H:%M") if request.user.last_login else "—",
        "two_factor_enabled": False,
        "prefs": {},
    }

    return render(request, "pages/profile.html", context)