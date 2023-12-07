from django.db import models

# Create your models here.
class Customers(models.Model):
    name = models.CharField(max_length = 255)
    password = models.CharField(max_length = 255)
    billing_address = models.CharField(max_length = 255)