
from .views import product, category , product_type_create , sales_view
from django.urls import path

urlpatterns = [
    path('product/', product, name='product'),
    path('category/', category, name='category'),
    path("product-types/create/", product_type_create, name="product_type_create"),
    path('sales/', sales_view, name='sales'),  # Assuming sales view is the same as product view for now
]