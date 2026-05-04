from django.db import models

from admin_panel.models import Supplier, Product
from login.models import Agent


# Agent Supplier Model
class AgentSupp(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=15, default="Inactive")


# Delivery Round Model
class DeliveryRound(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    start_place = models.CharField(max_length=20)
    end_place = models.CharField(max_length=20)

    def __str__(self):
        return f"Round #{self.id}: {self.start_place} → {self.end_place}"


# Delivery Stock Model
class DeliveryStock(models.Model):
    delivery_round = models.ForeignKey(DeliveryRound, on_delete=models.CASCADE, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    no_of_copies = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x{self.no_of_copies} (Round #{self.delivery_round.id})"
