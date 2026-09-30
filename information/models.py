from django.db import models
# from django.contrib.auth.models import User
# from django.template.context_processors import debug
from .scripts.suppliercode import generate_supplier_code , reference_number_code
from decimal import Decimal

SUPPLIER_TYPE_CHOICES = [
    ('local', 'Local'),
    ('international', 'International'),
]

SUPPLIER_TYPE_COMPANY_CHOICES = [
    ('manufacturer', 'Manufacturer'),
    ('distributor', 'Distributor'),
    ('wholesaler', 'Wholesaler'),
    ('retailer', 'Retailer'),
]

SUPPLIER_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

SUPPLIER_COMPANY = [
    ('private', 'Private'),
    ('public', 'Public'),
    ('government', 'Government'),
    ('non-profit', 'Non-Profit'),
    ('individual', 'Individual'),
]


PAYMENT_STATUS_CHOICES = [
    ('paid', 'Paid'),
    ('unpaid', 'Unpaid'),
    ('pending', 'Pending'),
]


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
    supplier_type = models.CharField(max_length=100, choices=SUPPLIER_TYPE_CHOICES)
    supplier_type_company = models.CharField(max_length=100, choices=SUPPLIER_TYPE_COMPANY_CHOICES)
    supplier_status = models.CharField(max_length=100, choices=SUPPLIER_STATUS_CHOICES)
    supplier_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Enter the supplier rating (0.00 to 5.00)")
    supplier_company = models.CharField(max_length=200 , choices=SUPPLIER_COMPANY)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True) # its optional but for future reference we can use it to store any additional information about the supplier
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    

TRANSACTION_TYPE_CHOICES = [
    ("cash", "Cash"),
    ("credit", "Credit"),
    ("bank_transfer", "Bank Transfer"),
    ("mobile_payment", "Mobile Payment"),
]

EXPENSE_TYPE_CHOICES = [
    ("office", "Office"),
    ("personal", "Personal"),
]

PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("cancelled", "Cancelled"),
]


class ExpenseModel(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=reference_number_code,
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    # Fixed VAT/tax rate: 13%
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        default=Decimal("13.00"),
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
        default="office",
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPE_CHOICES,
        default="cash",
    )

    image = models.ImageField(
        upload_to="expense_images/",
        blank=True,
        null=True,
    )

    attachment_file = models.FileField(
        upload_to="expense_files/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.reference_number} - {self.name}"
    

class ExpansionTarget(models.Model):
    expansion_mrr_target = models.DecimalField(max_digits=12, decimal_places=2)
    new_market_target = models.DecimalField(max_digits=12, decimal_places=2)
    expansion_customers_target = models.PositiveIntegerField()
    penetration_goal = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)