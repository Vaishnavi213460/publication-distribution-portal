from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Product


class CustomerOrder(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('placed', 'Placed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    order_date = models.DateField(auto_now_add=True)  # auto set
    delivery_start_date = models.DateField(null=True, blank=True)
    delivery_end_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"


class OrderCart(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    qty = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default='cart')

    def __str__(self):
        return f"{self.product.name} x {self.qty}"

    class Meta:
        unique_together = ['order', 'product']