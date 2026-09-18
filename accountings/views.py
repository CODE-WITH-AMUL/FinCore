from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Product, Category, product_type


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
        # description = request.POST.get("description", "")
        if name:
            product_type.objects.create(name=name)
        return redirect("product")
    return redirect("product")