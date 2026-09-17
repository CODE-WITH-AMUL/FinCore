from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Product, Category


@login_required
def product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        types_of_product = request.POST.getlist("types_of_product")
        price = request.POST.get("price")
        image = request.POST.get("image")
        category = request.POST.get("category")
        manufacturer = request.POST.get("manufacturer")

        Product.objects.create(
            name=name,
            decription=description,
            types_of_product=types_of_product,
            price=price,
            image=image,
            category=category,
            manufacturer=manufacturer,
        )

        return redirect("product")

    products = Product.objects.all()

    return render(
        request,
        "server/product.html",
        {"products": products}
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

    categories = Category.objects.all()

    return render(
        request,
        "server/category.html",
        {"categories": categories}
    )