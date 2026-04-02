from django.db import models

from admin_panel.models import Supplier
from login.models import Agent


# Agent Supplier Model
class AgentSupp(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=15, default="Inactive")
