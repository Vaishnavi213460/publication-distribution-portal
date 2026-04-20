from django.contrib.auth.models import User
from django.db import models
from admin_panel.models import Location

# Role Model

class Role(models.Model):
    role = models.CharField(max_length=50)
    login = models.OneToOneField(User, on_delete=models.CASCADE)

# Agent Model
class Agent(models.Model):
    name = models.CharField(max_length=15)
    code = models.IntegerField()
    address = models.TextField(max_length=250)
    phone = models.IntegerField(max_length=15)
    photo = models.FileField(upload_to='images/', null=True, blank=True)
    forget_question = models.TextField(max_length=50)
    forget_question_answer = models.TextField(max_length=50)
    total_customers = models.IntegerField()
    status = models.CharField(max_length=10, default='Inactive')
    login = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    location = models.ManyToManyField(Location, blank=True)

    def __str__(self):
        return self.name   

# Customer Model

class Customer(models.Model):
    name = models.CharField(max_length=15)
    address = models.TextField(max_length=250)
    phone = models.IntegerField(max_length=15)
    email = models.EmailField()
    status = models.CharField(max_length=10, default='Inactive')
    login = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
