from django.db import models
from django.contrib.auth.models import User
from .scripts.unique import generate_invoice_number, generate_product_code, generate_isp_code, generate_sales_sku
from information.models import SupplierModel
from accounts.models import Customer

class Category(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()
    code_prefex = models.CharField(max_length=10, unique=True) # Unique code prefix for the category
    
    
    def __str__(self):
        return f"{self.name} ({self.code_prefex})"

class product_type(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()
    sku = models.CharField(max_length=50, unique=True , editable=False , default=generate_product_code) # Stock Keeping Unit
    isp_code = models.CharField(max_length=50, unique=True , editable=False , default=generate_isp_code) # International Standard Product Code
    types_of_product = models.ManyToManyField(product_type, related_name='products_list')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    manufacturer = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0, help_text="Enter the available quantity of the product")
    price = models.DecimalField(max_digits=10, decimal_places=2 , default=0.00 , help_text="Enter the price of the product")
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    stock = models.IntegerField(default=0, help_text="Enter the available stock quantity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"""
    
    Product Name: {self.name}
    SKU: {self.sku}
    ISP Code: {self.isp_code}"""
    
    
    
'''
This model is for the sales

'''

TYPES_OF_SALES = (
    ("b2b", "B2B"),
    ("b2c", "B2C"),
)

PAYMENT_STATUS_CHOICES = [
    ("paid", "Paid"),
    ("unpaid", "Unpaid"),
    ("pending", "Pending"),
]

PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash"),
    ("credit_card", "Credit Card"),
    ("bank_transfer", "Bank Transfer"),
    ("mobile_payment", "Mobile Payment"),
]

LOCATION_CHOICES = [
    ("inside", "Inside"),
    ("outside", "Outside"),
]


# ============================================================
# SALES MODEL
# ============================================================
class SalesModel(models.Model):
    """
    A single sales record. Stores a snapshot of the sale at the time it
    was created (price, discount, VAT, total). Does NOT auto-update if
    the linked Product's price changes later.

    Field semantics:
      - vat_amount        → VAT amount in Rupees (NOT a percentage)
      - discount_percentage → percentage (0–100)
      - discount_amount   → Rupees
      - total_amount      → Rupees (subtotal - discount + VAT)
    """

    sales_sku = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=generate_sales_sku,
        help_text="Stock Keeping Unit — auto-generated.",
    )

    # ---------- Customer (denormalised — swap to FK later if needed) ----------
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)

    # ---------- Relations ----------
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="sales",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="sales",
    )
    supplier = models.ForeignKey(
        SupplierModel,
        on_delete=models.CASCADE,
        related_name="sales",
    )

    # ---------- Classification ----------
    sales_types = models.CharField(max_length=10, choices=TYPES_OF_SALES)
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES)

    # ---------- Pricing ----------
    quantity = models.IntegerField(
        default=0,
        help_text="Enter the quantity of the product sold",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Unit price at the time of sale",
    )
    vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="VAT amount in Rs. (computed from VAT % at save time)",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Discount rate in %",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Discount amount in Rs.",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Final amount in Rs. (subtotal − discount + VAT)",
    )

    # ---------- Payment ----------
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cash",
    )

    # ---------- Timestamps ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def __str__(self):
        return f"{self.sales_sku} - {self.customer_name or 'Unknown'}"
    
    

