# models.py
from django.contrib.auth.models import User
from django.db import models


class DeliveryPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(null=True, blank=True) 
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True) 
 
     
    def __str__(self):
        return self.user.username


class Order(models.Model):
    STATUS_CHOICES = [
        ("Placed", "Placed"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Pending", "Pending"),
    ]

    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    delivery_person = models.ForeignKey(
    DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)
    
   
    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"


