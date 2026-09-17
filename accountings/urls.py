from .views import product, category
from django.urls import path

urlpatterns = [
    path('product/', product, name='product'),
    path('category/', category, name='category')
]