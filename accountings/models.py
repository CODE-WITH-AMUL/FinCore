import decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from .scripts.unique import (
    generate_invoice_number,
    generate_product_code,
    generate_isp_code,
    generate_sales_sku,
    purchases_number,
)
from information.models import SupplierModel


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()  # NOTE: typo kept for DB compat
    code_prefex = models.CharField(max_length=10, unique=True)  # NOTE: typo kept

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.code_prefex})"


# ============================================================
# PRODUCT TYPE
# ============================================================

class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ============================================================
# PRODUCT
# ============================================================

class Product(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()  # NOTE: typo kept for DB compat

    sku = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=generate_product_code,
    )
    isp_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=generate_isp_code,
    )
    types_of_product = models.ManyToManyField(ProductType, related_name='products_list')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )
    manufacturer = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0, help_text="Available quantity")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Price of the product",
    )
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    stock = models.IntegerField(default=0, help_text="Available stock quantity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Product: {self.name} | SKU: {self.sku} | ISP: {self.isp_code}"


# ============================================================
# SALES constants
# ============================================================

TYPES_OF_SALES = (
    ("b2b", "B2B"),
    ("b2c", "B2C"),
)

SALES_PAYMENT_STATUS_CHOICES = [
    ("paid", "Paid"),
    ("unpaid", "Unpaid"),
    ("pending", "Pending"),
]

SALES_PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash"),
    ("credit_card", "Credit Card"),
    ("bank_transfer", "Bank Transfer"),
    ("mobile_payment", "Mobile Payment"),
]

SALES_LOCATION_CHOICES = [
    ("inside", "Inside"),
    ("outside", "Outside"),
]


# ============================================================
# PURCHASES constants
# ============================================================

TYPES_OF_PURCHASES = [
    ("cash", "Cash Purchase"),
    ("credit", "Credit Purchase"),
    ("online", "Online Purchase"),
    ("consignment", "Consignment"),
]

PURCHASE_LOCATION_CHOICES = [
    ("kathmandu", "Kathmandu"),
    ("pokhara", "Pokhara"),
    ("lalitpur", "Lalitpur"),
    ("bhaktapur", "Bhaktapur"),
    ("other", "Other"),
]

PURCHASE_PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("partial", "Partial"),
    ("paid", "Paid"),
    ("overdue", "Overdue"),
]

PURCHASE_PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash"),
    ("bank", "Bank Transfer"),
    ("mobile", "Mobile Payment"),
    ("cheque", "Cheque"),
    ("credit", "Credit"),
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
      - vat_amount          → VAT amount in Rupees (NOT a percentage)
      - discount_percentage → percentage (0–100)
      - discount_amount     → Rupees
      - total_amount        → Rupees (subtotal - discount + VAT)
    """

    sales_sku = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=generate_sales_sku,
        help_text="Stock Keeping Unit — auto-generated.",
    )

    # ---------- Customer (denormalised) ----------
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

    # ---------- Classification (FIXED: sales choices now) ----------
    sales_types = models.CharField(
        max_length=20,
        choices=TYPES_OF_SALES,
    )
    location = models.CharField(
        max_length=20,
        choices=SALES_LOCATION_CHOICES,
    )

    # ---------- Pricing ----------
    quantity = models.IntegerField(
        default=0,
        help_text="Quantity of the product sold",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Unit price at the time of sale",
    )
    vat_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="VAT amount in Rs.",
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Discount rate in %",
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Discount amount in Rs.",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Final amount in Rs. (subtotal − discount + VAT)",
    )

    # ---------- Payment (FIXED: sales choices now) ----------
    payment_status = models.CharField(
        max_length=20,
        choices=SALES_PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=SALES_PAYMENT_METHOD_CHOICES,
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


# ============================================================
# PURCHASES MODEL
# ============================================================

class Purchases(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    supplier = models.ForeignKey(
        SupplierModel,
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    quantity = models.IntegerField(default=0, help_text="Quantity purchased")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Unit price at time of purchase",
    )
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        default=generate_invoice_number,
        help_text="Invoice number",
    )
    purchase_type = models.CharField(
        max_length=20,   # FIXED: was 10 — too short for "consignment"
        choices=TYPES_OF_PURCHASES,
    )
    location = models.CharField(
        max_length=20,   # FIXED: was 10 — bumped for safety
        choices=PURCHASE_LOCATION_CHOICES,
    )
    purchase_number = models.CharField(
        max_length=100,
        unique=True,
        default=purchases_number,
        help_text="Purchase number",
    )
    purchase_date = models.DateField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,   # FIXED: was 10 — "pending"/"partial"/"overdue" fit, but consistent
        choices=PURCHASE_PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PURCHASE_PAYMENT_METHOD_CHOICES,
        default="cash",
    )
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"

    def __str__(self):
        return self.purchase_number


# ============================================================
# PURCHASES ITEMS
# ============================================================

class PurchasesItems(models.Model):
    purchases = models.ForeignKey(
        Purchases,
        on_delete=models.CASCADE,
        related_name="purchase_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="purchase_items",
    )
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Purchase Item"
        verbose_name_plural = "Purchase Items"

    def __str__(self):
        # FIXED: was self.purchase.purchase_number → FK is self.purchases
        return f"{self.purchases.purchase_number} - {self.product}"


# ============================================================
# PURCHASE PAYMENT
# ============================================================

class PurchasePayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK = "bank", "Bank Transfer"
        MOBILE = "mobile", "Mobile Payment"

    purchase = models.ForeignKey(
        Purchases,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.01"))],
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        verbose_name = "Purchase Payment"
        verbose_name_plural = "Purchase Payments"

    def __str__(self):
        return f"{self.purchase.purchase_number} - {self.amount}"