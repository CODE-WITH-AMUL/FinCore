from django.urls import path
from .views import supplier_list


urlpatterns = [
    path('supplier/', supplier_list, name='supplier_list'),
]