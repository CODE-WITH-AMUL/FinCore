from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import SalesModel
from information.models import SupplierModel
from .models import Product, Category, product_type
import decimal

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

        # Get selected category
        category = get_object_or_404(Category, id=category_id)

        # Create product
        new_product = Product.objects.create(
            name=name,
            decription=description,
            price=price,
            image=image,
            category=category,
            manufacturer=manufacturer,
            stock=stock,
        )

        # Add many-to-many product types
        if types_of_product:
            new_product.types_of_product.set(types_of_product)

        return redirect("product")

    # Get all products
    products = Product.objects.all().order_by("-created_at")

    # Get all categories for the product form
    categories = Category.objects.all().order_by("name")

    # Get all product types for the product form
    product_types = product_type.objects.all().order_by("name")

    # Optional category filter
    selected_category = request.GET.get("category")

    if selected_category:
        products = products.filter(category_id=selected_category)

    return render(
        request,
        "server/product.html",
        {
            "products": products,
            "categories": categories,
            "product_types": product_types,
            "selected_category": selected_category,
        },
    )


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

    return render(
        request,
        "server/category.html",
        {
            "categories": categories,
        },
    )
    
    
@login_required
def product_type_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            product_type.objects.create(name=name)
        return redirect("product")
    return redirect("product")


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
        vat_amount_raw = request.POST.get("vat_amount")  # this is the VAT %
        discount_percentage = request.POST.get("discount_percentage")
        supplier_id = request.POST.get("supplier")
        payment_method = request.POST.get("payment_method")
        payment_status = request.POST.get("payment_status")

        product = get_object_or_404(Product, pk=product_id)
        category = get_object_or_404(Category, pk=category_id)
        supplier = get_object_or_404(SupplierModel, pk=supplier_id)

        # ---------- SERVER-SIDE RECALCULATION (source of truth) ----------
        qty = decimal.Decimal(str(quantity or 0))
        pr = decimal.Decimal(str(price or 0))
        dp = decimal.Decimal(str(discount_percentage or 0))
        vat_pct = decimal.Decimal(str(vat_amount_raw or 0))

        subtotal = qty * pr
        discount_amount = (subtotal * dp) / decimal.Decimal(100)
        discounted = subtotal - discount_amount
        vat_rs = (discounted * vat_pct) / decimal.Decimal(100)
        total_amount = discounted + vat_rs

        SalesModel.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            product=product,
            quantity=qty,
            category=category,
            sales_types=sales_types,
            location=location,
            price=pr,
            vat_amount=vat_rs,                 # store Rs. amount
            discount_percentage=dp,
            discount_amount=discount_amount,
            total_amount=total_amount,
            supplier=supplier,
            payment_method=payment_method,
            payment_status=payment_status,
        )
        return redirect("sales")

    # ---------- GET: build context ----------
    sales_qs = (
        SalesModel.objects
        .select_related("product", "category", "supplier")
        .order_by("-created_at")
    )

    # KPIs (safe — works even if table is empty)
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


# ============================================================
# UTILITY — NOT A VIEW (no @login_required)
# ============================================================
def discount_price(price, discount_percentage):
    """Return (final_price, discount_amount) after applying discount %."""
    price = decimal.Decimal(str(price))
    discount_percentage = decimal.Decimal(str(discount_percentage))
    discount_amount = (price * discount_percentage) / decimal.Decimal(100)
    final_price = price - discount_amount
    return final_price, discount_amount
