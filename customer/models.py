from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Product, Frequency
from login.models import Agent
from datetime import date


class CustomerOrder(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Cart'),
        ('order_confirmed', 'Order Confirmed'),
        ('payment_received', 'Payment Received'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('one_time', 'One-time'),
        ('monthly', 'Monthly'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    payment_type = models.CharField(
        max_length=10, choices=PAYMENT_TYPE_CHOICES, default='one_time'
    )

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

    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivering', 'Delivering'),
        ('paused', 'Paused — Payment Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    frequency = models.ForeignKey(
        Frequency, on_delete=models.SET_NULL, null=True, blank=True
    )
    frequency_months = models.PositiveIntegerField(default=1)
    qty = models.PositiveIntegerField(default=1)
    delivery_start_date = models.DateField(null=True, blank=True)
    delivery_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    delivery_status = models.CharField(
        max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending'
    )

    def total_amount(self):
        return float(self.product.price) * self.qty * self.frequency_months

    def monthly_amount(self):
        return float(self.product.price) * self.qty

    def months_paid(self):
        """Count of confirmed monthly payments for this order item."""
        return self.monthly_payments.filter(status='paid').count()

    def is_active_this_month(self):
        """
        Return True if the customer has a paid payment covering the current month,
        OR the order was one-time paid (payment_type='one_time' on the order).
        Used by the agent to decide whether to deliver today.
        """
        today = date.today()

        # One-time full payment — always active if within delivery window
        if self.order.payment_type == 'one_time' and self.order.status == 'payment_received':
            if self.delivery_start_date and self.delivery_end_date:
                return self.delivery_start_date <= today <= self.delivery_end_date
            return self.order.status == 'payment_received'

        # Monthly payment — check if current month has a paid record
        current_month_payment = self.monthly_payments.filter(
            status='paid',
            month_year__year=today.year,
            month_year__month=today.month,
        ).exists()
        return current_month_payment

    def __str__(self):
        freq_label = self.frequency.frequency if self.frequency else f"{self.frequency_months}mo"
        return f"{self.product.name} x{self.qty} ({freq_label})"

    class Meta:
        unique_together = ['order', 'product']


class MonthlyPayment(models.Model):
    """Tracks each monthly payment instalment for monthly-payment orders."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    order_item = models.ForeignKey(
        OrderCart, on_delete=models.CASCADE, related_name='monthly_payments'
    )
    month_year = models.DateField(
        help_text="First day of the month this payment covers. E.g. 2026-04-01"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"Payment for {self.order_item.product.name} "
            f"— {self.month_year.strftime('%b %Y')} [{self.status}]"
        )

    class Meta:
        unique_together = ['order_item', 'month_year']
        ordering = ['month_year']


class DailyDeliveryLog(models.Model):
    """Agent marks each day's delivery for each order item."""
    STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('missed', 'Missed'),
        ('holiday', 'Customer Holiday'),
    ]
    order_item = models.ForeignKey(
        OrderCart, on_delete=models.CASCADE, related_name='delivery_logs'
    )
    delivery_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='delivered')
    note = models.CharField(max_length=200, blank=True)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='delivery_logs_marked'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_item.product.name} — {self.delivery_date} [{self.status}]"

    class Meta:
        unique_together = ['order_item', 'delivery_date']
        ordering = ['-delivery_date']


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


class Complaint(models.Model):
    """Customer complaints against agents."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Review', 'In Review'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='complaints'
    )
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name='complaints'
    )
    complaint = models.CharField(max_length=50)
    comp_date = models.DateField(auto_now_add=True)
    comp_reply = models.CharField(max_length=50, default='')
    comp_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='Pending'
    )

    def __str__(self):
        return f"Complaint #{self.id} — {self.customer.username} vs {self.agent.name}"
