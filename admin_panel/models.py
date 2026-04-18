from django.contrib.auth.models import User
from django.db import models

# Location model
class Location(models.Model):
    location = models.CharField(max_length=20)

    def __str__(self):
        return self.location

# Frequency model
class Frequency(models.Model):
    frequency = models.CharField(max_length=20)

    def __str__(self):
        return self.frequency

# Product Model
class Product(models.Model):
    type = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_from = models.CharField(max_length=20)
    management_type = models.CharField(max_length=50)
    issue_day = models.DateField()
    details = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    frequency = models.ManyToManyField(Frequency, blank=True)

    def __str__(self):
        return self.name


# supplier Model
class Supplier(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    address = models.TextField()
    phone = models.IntegerField()
    status = models.CharField(max_length=15, default="Inactive")
    product = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.name







