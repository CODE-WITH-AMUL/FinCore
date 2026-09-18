from .models import CompanyInformation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def company_profile(request, id=None):
    # Fetch or create the singleton company record
    company_info = CompanyInformation.objects.first()

    if request.method == "POST":
        company_name = request.POST.get("company_name", "").strip()
        company_address = request.POST.get("company_address", "").strip()
        company_email = request.POST.get("company_email", "").strip()
        company_phone = request.POST.get("company_phone", "").strip()
        company_office_type = request.POST.get("company_office_type", "").strip()
        company_logo = request.FILES.get("company_logo")

        if company_info is None:
            company_info = CompanyInformation()

        company_info.company_name = company_name
        company_info.company_address = company_address
        company_info.company_email = company_email
        company_info.company_phone = company_phone
        company_info.company_office_type = company_office_type
        if company_logo:
            company_info.company_logo = company_logo
        company_info.save()

        messages.success(request, "Company profile updated successfully.")
        return redirect("company_profile")

    return render(
        request,
        "pages/company_profile.html",
        {"company_info": company_info},
    )