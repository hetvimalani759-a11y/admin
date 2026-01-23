from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from delivery.models import DeliveryPerson 

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} → {self.name}"



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = models.IntegerField()
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=100)

    def __str__(self):
        return self.name




# Lenses
class Lens(models.Model):
    LENS_TYPE = (
        ('single', 'Single Vision'),
        ('bifocal', 'Bifocal'),
        ('progressive', 'Progressive'),
    )

    name = models.CharField(max_length=200)
    lens_type = models.CharField(max_length=20, choices=LENS_TYPE)
    power_range = models.CharField(max_length=50)
    price = models.IntegerField()

    def __str__(self):
        return self.name


# Orders
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

   

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    title=models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    gst_number = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError("Only one CompanyInfo instance allowed")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
      # ✅ allowed here

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(
        DeliveryPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

