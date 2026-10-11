from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from information.models import SupplierModel

from .models import (
    Category,
    Product,
    ProductType,
    SalesModel,
    Purchases,
    PurchasesItems,
    PurchasePayment,
    TYPES_OF_PURCHASES,
    PURCHASE_LOCATION_CHOICES,
    PURCHASE_PAYMENT_STATUS_CHOICES,
    PURCHASE_PAYMENT_METHOD_CHOICES,
)
from .scripts.unique import (
    generate_invoice_number,
    purchases_number,
)


# ============================================================
# PRODUCT
# ============================================================

@login_required
def product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        types_of_product = request.POST.getlist("types_of_product")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        category_id = request.POST.get("category")
        manufacturer = request.POST.get("manufacturer")
        stock = request.POST.get("stock")

        category_obj = get_object_or_404(Category, id=category_id)

        new_product = Product.objects.create(
            name=name,
            decription=description,
            price=price,
            image=image,
            category=category_obj,
            manufacturer=manufacturer,
            stock=stock,
        )

        if types_of_product:
            new_product.types_of_product.set(types_of_product)

        return redirect("product")

    products = Product.objects.all().order_by("-created_at")
    categories = Category.objects.all().order_by("name")
    product_types = ProductType.objects.all().order_by("name")

    selected_category = request.GET.get("category")
    if selected_category:
        products = products.filter(category_id=selected_category)

    return render(request, "server/product.html", {
        "products": products,
        "categories": categories,
        "product_types": product_types,
        "selected_category": selected_category,
    })


# ============================================================
# CATEGORY
# ============================================================

@login_required
def category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        code_prefix = request.POST.get("code_prefix")

        Category.objects.create(
            name=name,
            decription=description,
            code_prefex=code_prefix,
        )
        return redirect("category")

    categories = Category.objects.all().order_by("name")
    return render(request, "server/category.html", {"categories": categories})


# ============================================================
# PRODUCT TYPE
# ============================================================

@login_required
def product_type_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            ProductType.objects.create(name=name)
    return redirect("product")


# ============================================================
# SALES
# ============================================================

@login_required
def sales_view(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        customer_email = request.POST.get("customer_email")
        customer_phone = request.POST.get("customer_phone")
        product_id = request.POST.get("product")
        quantity = request.POST.get("quantity")
        category_id = request.POST.get("category")
        sales_types = request.POST.get("sales_types")
        location = request.POST.get("location")
        price = request.POST.get("price")
        vat_amount_raw = request.POST.get("vat_amount")
        discount_percentage = request.POST.get("discount_percentage")
        supplier_id = request.POST.get("supplier")
        payment_method = request.POST.get("payment_method")
        payment_status = request.POST.get("payment_status")

        product_obj = get_object_or_404(Product, pk=product_id)
        category_obj = get_object_or_404(Category, pk=category_id)
        supplier_obj = get_object_or_404(SupplierModel, pk=supplier_id)

        qty = Decimal(str(quantity or 0))
        pr = Decimal(str(price or 0))
        dp = Decimal(str(discount_percentage or 0))
        vat_pct = Decimal(str(vat_amount_raw or 0))

        subtotal = qty * pr
        discount_amount = (subtotal * dp) / Decimal(100)
        discounted = subtotal - discount_amount
        vat_rs = (discounted * vat_pct) / Decimal(100)
        total_amount = discounted + vat_rs

        SalesModel.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            product=product_obj,
            quantity=int(qty),
            category=category_obj,
            sales_types=sales_types,
            location=location,
            price=pr,
            vat_amount=vat_rs,
            discount_percentage=dp,
            discount_amount=discount_amount,
            total_amount=total_amount,
            supplier=supplier_obj,
            payment_method=payment_method,
            payment_status=payment_status,
        )
        return redirect("sales")

    sales_qs = (
        SalesModel.objects
        .select_related("product", "category", "supplier")
        .order_by("-created_at")
    )

    total_sales = sum((s.total_amount or 0) for s in sales_qs)
    total_orders = sales_qs.count()
    avg_order = (total_sales / total_orders) if total_orders else 0
    outstanding = sum(
        (s.total_amount or 0)
        for s in sales_qs
        if s.payment_status in ("pending", "unpaid")
    )

    context = {
        "sales": sales_qs,
        "products": Product.objects.all(),
        "categories": Category.objects.all(),
        "suppliers": SupplierModel.objects.all(),
        "total_sales": f"{total_sales:,.2f}",
        "total_orders": total_orders,
        "avg_order": f"{avg_order:,.2f}",
        "outstanding": f"{outstanding:,.2f}",
    }
    return render(request, "server/sales.html", context)


def discount_price(price, discount_percentage):
    price = Decimal(str(price))
    discount_percentage = Decimal(str(discount_percentage))
    discount_amount = (price * discount_percentage) / Decimal(100)
    final_price = price - discount_amount
    return final_price, discount_amount


# ============================================================
# PURCHASES — MAIN VIEW (create + list + edit-in-place)
# ============================================================

@login_required
def Purchases_view(request):
    edit_id = request.GET.get('edit')

    if request.method == "POST":
        try:
            with transaction.atomic():
                # ---------- Parent purchase fields ----------
                supplier_id = request.POST.get('supplier')
                invoice_number = request.POST.get('invoice_number') or generate_invoice_number()
                purchase_type = request.POST.get('purchase_type')
                location = request.POST.get('location')
                purchase_number = request.POST.get('purchase_number') or purchases_number()
                payment_status = request.POST.get('payment_status', 'pending')
                payment_method = request.POST.get('payment_method', 'cash')
                notes = request.POST.get('notes', '')

                discount_percentage = Decimal(request.POST.get('discount_percentage') or '0')
                paid_amount = Decimal(request.POST.get('paid_amount') or '0')

                # Line item arrays
                product_ids = request.POST.getlist('product[]')
                quantities = request.POST.getlist('quantity[]')
                unit_prices = request.POST.getlist('unit_price[]')
                item_discounts = request.POST.getlist('item_discount_percentage[]')
                item_vats = request.POST.getlist('item_vat_amount[]')

                if not supplier_id:
                    raise ValueError("Supplier is required.")

                first_product_id = next((pid for pid in product_ids if pid), None)
                if not first_product_id:
                    raise ValueError("At least one product must be selected.")

                first_qty = int(quantities[0]) if quantities else 0
                first_price = Decimal(unit_prices[0] or '0') if unit_prices else Decimal('0')

                if edit_id:
                    # ----- EDIT existing purchase -----
                    purchase = get_object_or_404(Purchases, pk=edit_id)
                    purchase.supplier_id = supplier_id
                    purchase.product_id = first_product_id
                    purchase.quantity = first_qty
                    purchase.price = first_price
                    purchase.invoice_number = invoice_number
                    purchase.purchase_type = purchase_type
                    purchase.location = location
                    purchase.purchase_number = purchase_number
                    purchase.payment_status = payment_status
                    purchase.payment_method = payment_method
                    purchase.notes = notes
                    purchase.discount_percentage = discount_percentage
                    purchase.paid_amount = paid_amount
                    purchase.save()

                    # Replace line items
                    purchase.purchase_items.all().delete()
                else:
                    # ----- CREATE new purchase -----
                    purchase = Purchases.objects.create(
                        supplier_id=supplier_id,
                        product_id=first_product_id,
                        quantity=first_qty,
                        price=first_price,
                        invoice_number=invoice_number,
                        purchase_type=purchase_type,
                        location=location,
                        purchase_number=purchase_number,
                        payment_status=payment_status,
                        payment_method=payment_method,
                        notes=notes,
                        discount_percentage=discount_percentage,
                        paid_amount=paid_amount,
                    )

                # ---------- Line items ----------
                subtotal_total = Decimal('0.00')
                vat_total = Decimal('0.00')

                for i in range(len(product_ids)):
                    if not product_ids[i]:
                        continue

                    qty = int(quantities[i] or 0)
                    unit_price = Decimal(unit_prices[i] or '0')
                    disc_pct = Decimal(item_discounts[i] or '0')
                    vat_amt = Decimal(item_vats[i] or '0')

                    line_gross = unit_price * qty
                    line_discount_amt = line_gross * disc_pct / Decimal('100')
                    line_subtotal = line_gross - line_discount_amt
                    line_total = line_subtotal + vat_amt

                    PurchasesItems.objects.create(
                        purchases=purchase,
                        product_id=product_ids[i],
                        quantity=qty,
                        unit_price=unit_price,
                        discount_percentage=disc_pct,
                        discount_amount=line_discount_amt,
                        vat_amount=vat_amt,
                        subtotal_amount=line_subtotal,
                        total_amount=line_total,
                    )

                    subtotal_total += line_subtotal
                    vat_total += vat_amt

                # ---------- Totals ----------
                overall_discount_amt = subtotal_total * discount_percentage / Decimal('100')
                total_amount = subtotal_total - overall_discount_amt + vat_total
                due_amount = total_amount - paid_amount

                purchase.subtotal_amount = subtotal_total
                purchase.vat_amount = vat_total
                purchase.discount_amount = overall_discount_amt
                purchase.total_amount = total_amount
                purchase.due_amount = due_amount

                if due_amount <= 0 and purchase.payment_status == 'pending':
                    purchase.payment_status = 'paid'
                elif 0 < paid_amount < total_amount:
                    purchase.payment_status = 'partial'

                purchase.save()

                # Initial payment record only on create
                if not edit_id and paid_amount > 0:
                    PurchasePayment.objects.create(
                        purchase=purchase,
                        amount=paid_amount,
                        payment_method=payment_method,
                        payment_date=timezone.now().date(),
                        notes='Initial payment on purchase creation',
                    )

            if edit_id:
                messages.success(request, f"Purchase {purchase.purchase_number} updated successfully.")
            else:
                messages.success(request, f"Purchase {purchase.purchase_number} created successfully.")
            return redirect('purchases')

        except Exception as e:
            messages.error(request, f"Error saving purchase: {e}")
            # Fall through to render the page with the error

    # ---------- GET (and POST-with-error fallback) ----------
    purchases_qs = Purchases.objects.select_related('supplier').order_by('-created_at')

    totals = purchases_qs.aggregate(
        total=Sum('total_amount'),
        paid=Sum('paid_amount'),
        due=Sum('due_amount'),
    )

    # Edit-mode context
    edit_purchase = None
    edit_items = []
    if edit_id:
        edit_purchase = get_object_or_404(Purchases, pk=edit_id)
        edit_items = list(
            edit_purchase.purchase_items.select_related('product').all()
        )

    context = {
        "products": Product.objects.all(),
        "suppliers": SupplierModel.objects.all(),
        "purchases": purchases_qs[:25],
        "total_purchases": purchases_qs.count(),
        "total_purchase_amount": totals['total'] or 0,
        "total_paid": totals['paid'] or 0,
        "total_due": totals['due'] or 0,
        "pending_count": purchases_qs.filter(payment_status='pending').count(),
        "today": timezone.now().date(),
        "user": request.user,
        "company_name": getattr(request.user, 'company_name', 'Your Company'),

        "purchase_types": TYPES_OF_PURCHASES,
        "location_choices": PURCHASE_LOCATION_CHOICES,
        "payment_status_choices": PURCHASE_PAYMENT_STATUS_CHOICES,
        "payment_method_choices": PURCHASE_PAYMENT_METHOD_CHOICES,

        "next_invoice_number": generate_invoice_number(),
        "next_purchase_number": purchases_number(),

        # Edit mode
        "edit_purchase": edit_purchase,
        "edit_items": edit_items,
    }
    return render(request, "server/purchases.html", context)


# ============================================================
# PURCHASE — edit URL (redirects to ?edit=<id>)
# ============================================================

@login_required
def purchase_edit(request, pk):
    """Just redirect to the list view with ?edit=<id> so the inline form opens."""
    return redirect(f"/direct/accountings/purchases/?edit={pk}")


# ============================================================
# PURCHASE — delete
# ============================================================

@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchases, pk=pk)
    number = purchase.purchase_number
    purchase.delete()
    messages.success(request, f"Purchase {number} deleted.")
    return redirect('purchases')


# ============================================================
# PURCHASE — PDF / PNG / Print stubs (upgrade later)
# ============================================================

@login_required
def purchase_pdf(request, pk):
    return HttpResponse(f"PDF export for purchase #{pk} coming soon.", status=200)


@login_required
def purchase_png(request, pk):
    return HttpResponse(f"Image export for purchase #{pk} coming soon.", status=200)


@login_required
def purchase_print(request, pk):
    purchase = get_object_or_404(
        Purchases.objects.select_related('supplier').prefetch_related('purchase_items__product'),
        pk=pk,
    )
    return render(request, "server/purchase_print.html", {"purchase": purchase})