from django.db import models
from django.contrib.auth.models import User

# class Sales(models.Model):
#     user = models.ForeignKey(User, on_delete=models.Casecade , related_name='sales')




class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True) # Stock Keeping Unit
    types_of_product = models.CharField(max_length = 100)
    