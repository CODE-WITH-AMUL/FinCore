from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import CompanyInformation, UserProfileData


@login_required
def userprofile(request):

    try:
        user_profile = UserProfileData.objects.get(
            user=request.user
        )
    except UserProfileData.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("home")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        company_id = request.POST.get("company")
        bio = request.POST.get("bio", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        user_profile.name = name
        user_profile.bio = bio

        # Update company
        if company_id:
            try:
                company = CompanyInformation.objects.get(
                    id=company_id
                )
                user_profile.company = company

            except CompanyInformation.DoesNotExist:
                messages.error(
                    request,
                    "Selected company does not exist."
                )
                return redirect("userprofile")

        # Update profile picture
        if profile_picture:
            user_profile.profile_picture = profile_picture

        user_profile.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("userprofile")

    company_info = user_profile.company

    context = {
        "user_profile": user_profile,
        "company_info": company_info,
    }

    return render(
        request,
        "pages/profile.html",
        context
    )


@login_required
def company_profile(request, company_id):

    try:
        company_info = CompanyInformation.objects.get(
            id=company_id
        )

    except CompanyInformation.DoesNotExist:
        messages.error(
            request,
            "Company information not found."
        )
        return redirect("home")

    context = {
        "company_info": company_info
    }

    return render(
        request,
        "accounts/company_profile.html",
        context
    )