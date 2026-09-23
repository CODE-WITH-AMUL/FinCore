from django.db import models
from django.contrib.auth.models import User
from .scripts.suppliercode import generate_supplier_code


class SupplierModel(models.Model):
    name = models.CharField(max_length=200)
    
    company_name = models.CharField(max_length=200)
    products_supplied = models.ManyToManyField('accountings.Product', related_name='suppliers')
    
    adress = models.TextField()
    city = models.CharField(max_length=100)
    provience = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    zip_code = models.CharField(max_length=20)
    History = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=50, unique=True , editable=False , default=generate_supplier_code) # Unique code for the supplier
    supplier_type = models.CharField(max_length=100, choices=[('local', 'Local'), ('international', 'International')])
    supplier_type_company = models.CharField(max_length=100, choices=[('manufacturer', 'Manufacturer'), ('distributor', 'Distributor'), ('wholesaler', 'Wholesaler'), ('retailer', 'Retailer')])
    supplier_status = models.CharField(max_length=100, choices=[('active', 'Active'), ('inactive', 'Inactive')])
    supplier_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Enter the supplier rating (0.00 to 5.00)")
    supplier_company = models.CharField(max_length=200 , choices=[('private', 'Private'), ('public', 'Public'), ('government', 'Government' ), ('non-profit', 'Non-Profit') , ('individual', 'Individual')])
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=100, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('pending', 'Pending')])
    notes = models.TextField(blank=True, null=True) # its optional but for future reference we can use it to store any additional information about the supplier
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.code})"