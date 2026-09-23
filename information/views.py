from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import SupplierModel


@login_required
def supplier_list(request):

    context = {}

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        # ---------------- CREATE ----------------
        if action == "create":
            supplier = SupplierModel.objects.create(
                name=request.POST.get("name"),
                company_name=request.POST.get("company_name"),
                adress=request.POST.get("adress"),
                city=request.POST.get("city"),
                provience=request.POST.get("provience"),
                country=request.POST.get("country"),
                zip_code=request.POST.get("zip_code"),
                History=request.POST.get("History"),
                supplier_type=request.POST.get("supplier_type"),
                supplier_type_company=request.POST.get("supplier_type_company"),
                supplier_status=request.POST.get("supplier_status"),
                supplier_rating=request.POST.get("supplier_rating") or 0,
                supplier_company=request.POST.get("supplier_company"),
                email=request.POST.get("email"),
                contact_number=request.POST.get("contact_number"),
                payment_status=request.POST.get("payment_status"),
                notes=request.POST.get("notes"),
            )
            products = request.POST.getlist("products_supplied")
            if products:
                supplier.products_supplied.set(products)

            messages.success(request, "Supplier created.")
            return redirect("supplier_list")
        
        if action == "update":
            pk = request.POST.get("pk")
            supplier = get_object_or_404(SupplierModel, pk=pk)

            supplier.name                  = request.POST.get("name", supplier.name).strip()
            supplier.company_name          = request.POST.get("company_name", supplier.company_name).strip()
            supplier.adress                = request.POST.get("adress", supplier.adress).strip()
            supplier.city                  = request.POST.get("city", supplier.city).strip()
            supplier.provience             = request.POST.get("provience", supplier.provience).strip()
            supplier.country               = request.POST.get("country", supplier.country).strip()
            supplier.zip_code              = request.POST.get("zip_code", supplier.zip_code).strip()
            supplier.History               = request.POST.get("History", supplier.History or "").strip()
            supplier.supplier_type         = request.POST.get("supplier_type", supplier.supplier_type).strip()
            supplier.supplier_type_company = request.POST.get("supplier_type_company", supplier.supplier_type_company).strip()
            supplier.supplier_status       = request.POST.get("supplier_status", supplier.supplier_status).strip()
            supplier.supplier_company      = request.POST.get("supplier_company", supplier.supplier_company).strip()
            supplier.email                 = request.POST.get("email", supplier.email).strip()
            supplier.contact_number        = request.POST.get("contact_number", supplier.contact_number).strip()
            supplier.payment_status        = request.POST.get("payment_status", supplier.payment_status).strip()
            supplier.notes                 = request.POST.get("notes", supplier.notes or "").strip()

            rating = request.POST.get("supplier_rating", "").strip()
            if rating:
                supplier.supplier_rating = rating

            supplier.save()
            messages.success(request, f'Supplier "{supplier.name}" updated.')
            return redirect("supplier_list")
        # ---------------- DELETE ----------------
        if action == "delete":
            pk = request.POST.get("pk")
            SupplierModel.objects.filter(pk=pk).delete()
            messages.success(request, "Supplier deleted.")
            return redirect("supplier_list")

        # ---------------- TOGGLE ----------------
        if action == "toggle":
            pk = request.POST.get("pk")
            supplier = get_object_or_404(SupplierModel, pk=pk)
            if supplier.supplier_status == "active":
                supplier.supplier_status = "inactive"
            else:
                supplier.supplier_status = "active"
            supplier.save()
            return redirect("supplier_list")

        # ---------------- SEARCH ----------------
        if action == "search":
            context["query"] = request.POST.get("search_query", "").strip()

    # ---------------- LIST ----------------
    suppliers = SupplierModel.objects.all().order_by("-created_at")

    query = context.get("query", "")
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_number__icontains=query) |
            Q(city__icontains=query) |
            Q(provience__icontains=query) |
            Q(country__icontains=query) |
            Q(zip_code__icontains=query)
        )

    page_obj = Paginator(suppliers, 10).get_page(request.GET.get("page"))

    context["supplier_list"] = page_obj
    context["page_obj"] = page_obj

    return render(request, "server/supplier_list.html", context)