from django.urls import path

from .views import expense_list, supplier_list

urlpatterns = [
    path("supplier/", supplier_list, name="supplier_list"),
    path("expense/", expense_list, name="expense_list"),
    path("expenses/", expense_list, name="expense_list_legacy"),
]