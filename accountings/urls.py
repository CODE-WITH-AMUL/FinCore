
from .views import ( 
product,
category , 
product_type_create ,
sales_view
)

from django.urls import path
from .views import (
    Purchases_view ,
    purchase_edit , 
    purchase_pdf , 
    purchase_png , 
    purchase_print , 
    purchase_delete)

urlpatterns = [
    path('product/', product, name='product'),
    path('category/', category, name='category'),
    path("product-types/create/", product_type_create, name="product_type_create"),
    path('sales/', sales_view, name='sales'),  
    path('purchases/', Purchases_view, name='purchases'),
    path('purchases/<int:pk>/edit/',  purchase_edit,  name='purchase_edit'),
    path('purchases/<int:pk>/delete/', purchase_delete, name='purchase_delete'),
    path('purchases/<int:pk>/pdf/',   purchase_pdf,   name='purchase_pdf'),
    path('purchases/<int:pk>/png/',   purchase_png,   name='purchase_png'),
    path('purchases/<int:pk>/print/', purchase_print, name='purchase_print'),
]