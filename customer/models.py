from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Product, Frequency


class CustomerOrder(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('order_confirmed', 'Order Confirmed'),
        ('payment_received', 'Payment Received'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')

    def __str__(self):
        return f"Order #{self.id} — {self.customer.username}"

    def get_total(self):
        return sum(item.total_amount() for item in self.items.all())

    def get_total_items(self):
        return sum(item.qty for item in self.items.all())


class OrderCart(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('order_confirmed', 'Order Confirmed'),
        ('payment_received', 'Payment Received'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Frequency is now a FK to the admin_panel Frequency model
    frequency = models.ForeignKey(
        Frequency,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Linked to admin_panel.Frequency"
    )
    # Derived month count — stored so we don't re-parse on every calc
    frequency_months = models.PositiveIntegerField(
        default=1,
        help_text="Month count derived from Frequency label"
    )

    qty = models.PositiveIntegerField(default=1)
    delivery_start_date = models.DateField(null=True, blank=True)
    delivery_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')

    def total_amount(self):
        """price × qty × frequency_months"""
        return float(self.product.price) * self.qty * self.frequency_months

    def __str__(self):
        freq_label = self.frequency.frequency if self.frequency else f"{self.frequency_months}mo"
        return f"{self.product.name} x{self.qty} ({freq_label})"

    class Meta:
        unique_together = ['order', 'product']


class ShippingDetails(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    shipping_address = models.TextField()
    landmark = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80)
    district = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, default='Kerala')
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.city}, {self.pincode}"

    def save(self, *args, **kwargs):
        if self.is_default:
            ShippingDetails.objects.filter(
                customer=self.customer, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Shipping Details'