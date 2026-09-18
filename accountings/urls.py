
from .views import product, category , product_type_create
from django.urls import path

urlpatterns = [
    path('product/', product, name='product'),
    path('category/', category, name='category'),
    # urls.py
    path("product-types/create/", product_type_create, name="product_type_create"),
]