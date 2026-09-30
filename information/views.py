from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, ExpressionWrapper, F, Sum, DecimalField
from django.http import JsonResponse
from django.utils import timezone

from calendar import month_abbr
from datetime import timedelta
from decimal import Decimal

from .models import SupplierModel, ExpenseModel


# ============================================================
# SUPPLIERS
# ============================================================
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

        # ---------------- UPDATE ----------------
        if action == "update":
            pk = request.POST.get("pk")
            supplier = get_object_or_404(SupplierModel, pk=pk)

            supplier.name = request.POST.get("name", supplier.name).strip()
            supplier.company_name = request.POST.get("company_name", supplier.company_name).strip()
            supplier.adress = request.POST.get("adress", supplier.adress).strip()
            supplier.city = request.POST.get("city", supplier.city).strip()
            supplier.provience = request.POST.get("provience", supplier.provience).strip()
            supplier.country = request.POST.get("country", supplier.country).strip()
            supplier.zip_code = request.POST.get("zip_code", supplier.zip_code).strip()
            supplier.History = request.POST.get("History", supplier.History or "").strip()
            supplier.supplier_type = request.POST.get("supplier_type", supplier.supplier_type).strip()
            supplier.supplier_type_company = request.POST.get("supplier_type_company", supplier.supplier_type_company).strip()
            supplier.supplier_status = request.POST.get("supplier_status", supplier.supplier_status).strip()
            supplier.supplier_company = request.POST.get("supplier_company", supplier.supplier_company).strip()
            supplier.email = request.POST.get("email", supplier.email).strip()
            supplier.contact_number = request.POST.get("contact_number", supplier.contact_number).strip()
            supplier.payment_status = request.POST.get("payment_status", supplier.payment_status).strip()
            supplier.notes = request.POST.get("notes", supplier.notes or "").strip()

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
            supplier.supplier_status = "inactive" if supplier.supplier_status == "active" else "active"
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


# ============================================================
# HELPERS
# ============================================================
def _amount_expression():
    """unit_price * quantity — the single source of truth for money."""
    return ExpressionWrapper(
        F("unit_price") * F("quantity"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )


def _sum_amount(queryset):
    """Sum unit_price * quantity over a queryset. Always returns a Decimal."""
    try:
        result = queryset.aggregate(total=Sum(_amount_expression()))["total"]
        return result if result is not None else Decimal("0")
    except Exception:
        return Decimal("0")


def _distinct_reference_count(queryset):
    """Count distinct reference numbers (used for expansion customer count)."""
    try:
        return queryset.values("reference_number").distinct().count()
    except Exception:
        return 0


def _month_labels(n=12):
    """Last n month labels ending at the current month. Format: 'Sep 25'."""
    now = timezone.now()
    y, m = now.year, now.month
    seq = []
    for _ in range(n):
        seq.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    seq.reverse()
    return [f"{month_abbr[m]} {str(y)[2:]}" for (y, m) in seq]

def _day_labels(n=7):
    """Last n day labels ending today. Format: '12 Sep'."""
    now = timezone.now()
    return [(now - timedelta(days=i)).strftime("%d %b") for i in range(n - 1, -1, -1)]


# ============================================================
# EXPANSION KPI PAYLOAD — feeds both the page and /api/
# ============================================================

def _build_expansion_kpi_payload():
    """
    Build the full payload from real ExpenseModel data.
    Every number here comes straight from the DB. No hardcoded values.
    """
    now = timezone.now()

    # ---------- Base querysets ----------
    all_expenses      = ExpenseModel.objects.all()
    paid_expenses     = all_expenses.filter(status="paid")
    pending_expenses  = all_expenses.filter(status="pending")
    office_expenses   = all_expenses.filter(expense_type="office")
    personal_expenses = all_expenses.filter(expense_type="personal")

    office_paid       = paid_expenses.filter(expense_type="office")

    # ---------- Expense KPI cards (real data) ----------
    total_expenses_amount   = _sum_amount(all_expenses)
    monthly_expenses_amount = _sum_amount(all_expenses.filter(
        created_at__year=now.year, created_at__month=now.month
    ))
    pending_expenses_amount = _sum_amount(pending_expenses)
    office_expenses_amount  = _sum_amount(office_expenses)

    office_count   = office_expenses.count()
    personal_count = personal_expenses.count()

    # ---------- Expansion cards ----------
    expansion_mrr       = _sum_amount(office_paid)
    new_market_revenue  = _sum_amount(paid_expenses)
    expansion_customers = _distinct_reference_count(office_expenses)

    total_records = all_expenses.count()
    penetration_pct = round(
        (expansion_customers / total_records) * 100, 2
    ) if total_records else 0.0

    # ---------- 12-month series ----------
    monthly_labels       = _month_labels(12)
    months               = list(monthly_labels)
    monthly_expense_data = []
    segment_a            = []   # Office paid
    segment_b            = []   # Personal paid
    segment_c            = []   # Pending

    # Walk backwards from the current month, 12 times, then reverse.
    seq = []
    y, m = now.year, now.month
    for _ in range(12):
        seq.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    seq.reverse()

    for (y, m) in seq:
        mq = all_expenses.filter(created_at__year=y, created_at__month=m)

        monthly_expense_data.append(float(_sum_amount(mq)))
        segment_a.append(float(_sum_amount(mq.filter(expense_type="office",   status="paid"))))
        segment_b.append(float(_sum_amount(mq.filter(expense_type="personal", status="paid"))))
        segment_c.append(float(_sum_amount(mq.filter(status="pending"))))
    # ---------- 7-day sparklines ----------
    spark_labels = _day_labels(7)

    def _daily_sum(queryset):
        out = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            out.append(float(_sum_amount(queryset.filter(created_at__date=d))))
        return out

    def _daily_customer_count():
        out = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            out.append(_distinct_reference_count(
                office_expenses.filter(created_at__date=d)
            ))
        return out

    mrr_trend         = _daily_sum(office_paid)
    market_trend      = _daily_sum(paid_expenses)
    customer_trend    = _daily_customer_count()
    penetration_trend = [
        round((c / total_records) * 100, 2) if total_records else 0.0
        for c in customer_trend
    ]

    # ---------- Optional ExpansionTarget ----------
    target = None
    try:
        from .models import ExpansionTarget  # noqa
        target = ExpansionTarget.objects.filter(active=True).order_by("-created_at").first()
    except Exception:
        target = None

    return {
        # Expense KPI cards
        "total_expenses":   float(total_expenses_amount),
        "monthly_expenses": float(monthly_expenses_amount),
        "pending_expenses": float(pending_expenses_amount),
        "office_expenses":  float(office_expenses_amount),
        "office_count":     office_count,
        "personal_count":   personal_count,

        # Expansion cards
        "expansion_mrr":              float(expansion_mrr),
        "expansion_mrr_target":       float(target.expansion_mrr_target) if target else 0.0,
        "new_market_revenue":         float(new_market_revenue),
        "new_market_target":          float(target.new_market_target) if target else 0.0,
        "expansion_customers":        expansion_customers,
        "expansion_customers_target": target.expansion_customers_target if target else 0,
        "penetration_pct":            penetration_pct,
        "penetration_goal":           float(target.penetration_goal) if target else 0.0,

        # 12-month charts
        "months":               months,
        "monthly_labels":       monthly_labels,
        "monthly_expense_data": monthly_expense_data,
        "segment_a":            segment_a,
        "segment_b":            segment_b,
        "segment_c":            segment_c,

        # 7-day sparklines
        "spark_labels":      spark_labels,
        "mrr_trend":         mrr_trend,
        "market_trend":      market_trend,
        "customer_trend":    customer_trend,
        "penetration_trend": penetration_trend,

        "updated_at": now.isoformat(),
    }


# @login_required
def expansion_kpis(request):
    """JSON endpoint polled every 15s by the front end."""
    try:
        payload = _build_expansion_kpi_payload()
    except Exception as e:
        payload = {"error": str(e), "updated_at": timezone.now().isoformat()}
    return JsonResponse(payload)


# ============================================================
# EXPENSE LIST
# ============================================================
@login_required
def expense_list(request):
    """GET: render page. POST: create expense."""

    if request.method == "POST":
        name             = request.POST.get("name", "").strip()
        unit_price       = request.POST.get("unit_price")
        quantity         = request.POST.get("quantity")
        status           = request.POST.get("status")
        expense_type     = request.POST.get("expense_type")
        transaction_type = request.POST.get("transaction_type")
        image            = request.FILES.get("image")
        attachment_file  = request.FILES.get("attachment_file")
        description      = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Expense name is required.")
            return redirect("expense_list")
        if not unit_price:
            messages.error(request, "Unit price is required.")
            return redirect("expense_list")
        if not quantity:
            messages.error(request, "Quantity is required.")
            return redirect("expense_list")

        try:
            expense = ExpenseModel.objects.create(
                name=name,
                unit_price=unit_price,
                quantity=quantity,
                tax_rate=Decimal("13.00"),
                status=status,
                expense_type=expense_type,
                transaction_type=transaction_type,
                image=image,
                attachment_file=attachment_file,
                description=description,
            )
            messages.success(request, f"Expense {expense.reference_number} created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating expense: {e}")
        return redirect("expense_list")

    # ---------- GET ----------
    expenses = ExpenseModel.objects.all().order_by("-created_at")

    try:
        kpi = _build_expansion_kpi_payload()
    except Exception:
        kpi = {
            "months": [], "monthly_labels": [], "monthly_expense_data": [],
            "segment_a": [], "segment_b": [], "segment_c": [],
            "expansion_mrr": 0.0, "expansion_mrr_target": 0.0,
            "new_market_revenue": 0.0, "new_market_target": 0.0,
            "expansion_customers": 0, "expansion_customers_target": 0,
            "penetration_pct": 0.0, "penetration_goal": 0.0,
            "spark_labels": [], "mrr_trend": [], "market_trend": [],
            "customer_trend": [], "penetration_trend": [],
            "total_expenses": 0.0, "monthly_expenses": 0.0,
            "pending_expenses": 0.0, "office_expenses": 0.0,
            "office_count": 0, "personal_count": 0,
        }

    context = {
        # Table
        "expense_list": expenses,

        # Expense KPI cards — real values straight from the DB
        "total_expenses":   kpi["total_expenses"],
        "monthly_expenses": kpi["monthly_expenses"],
        "pending_expenses": kpi["pending_expenses"],
        "office_expenses":  kpi["office_expenses"],
        "office_count":     kpi["office_count"],
        "personal_count":   kpi["personal_count"],

        # 12-month expense chart
        "monthly_labels":       kpi["monthly_labels"],
        "monthly_expense_data": kpi["monthly_expense_data"],

        # Expansion cards
        "expansion_mrr":              kpi["expansion_mrr"],
        "expansion_mrr_target":       kpi["expansion_mrr_target"],
        "new_market_revenue":         kpi["new_market_revenue"],
        "new_market_target":          kpi["new_market_target"],
        "expansion_customers":        kpi["expansion_customers"],
        "expansion_customers_target": kpi["expansion_customers_target"],
        "penetration_pct":            kpi["penetration_pct"],
        "penetration_goal":           kpi["penetration_goal"],

        # Stacked expansion chart
        "months":    kpi["months"],
        "segment_a": kpi["segment_a"],
        "segment_b": kpi["segment_b"],
        "segment_c": kpi["segment_c"],

        # Sparklines
        "spark_labels":      kpi["spark_labels"],
        "mrr_trend":         kpi["mrr_trend"],
        "market_trend":      kpi["market_trend"],
        "customer_trend":    kpi["customer_trend"],
        "penetration_trend": kpi["penetration_trend"],
    }

    return render(request, "server/expense_list.html", context)