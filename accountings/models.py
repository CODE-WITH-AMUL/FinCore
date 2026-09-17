from django.db import models
from django.contrib.auth.models import User
from .scripts.unique import generate_product_code, generate_isp_code

# class Sales(models.Model):
#     user = models.ForeignKey(User, on_delete=models.Casecade , related_name='sales')


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
    price = models.DecimalField(max_digits=10, decimal_places=2 , default=0.00 , help_text="Enter the price of the product")
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"""
    
    Product Name: {self.name}
    SKU: {self.sku}
    ISP Code: {self.isp_code}"""