from django.db import models
from django.contrib.auth.models import User
from delivery.models import DeliveryPerson
from django.utils import timezone

# ------------------ CATEGORY ------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ------------------ SUB CATEGORY ------------------
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} → {self.name}"


# ------------------ PRODUCT ------------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    def get_offer(self):
        now = timezone.now()
        return Offer.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).filter(
            models.Q(product=self) | models.Q(category=self.category)
        ).first()

    def get_final_price(self):
        offer = self.get_offer()
        if not offer:
            return self.price

        if offer.discount_type == 'percent':
            return self.price - (self.price * offer.discount_value / 100)
        else:
            return max(self.price - offer.discount_value, 0)

# ------------------ LENSES ------------------
class Lens(models.Model):
    LENS_TYPE = (
        ('single', 'Single Vision'),
        ('bifocal', 'Bifocal'),
        ('progressive', 'Progressive'),
    )

    name = models.CharField(max_length=200)
    lens_type = models.CharField(max_length=20, choices=LENS_TYPE)
    power_range = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# ------------------ 🔔 NOTIFICATIONS ------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ------------------ COMPANY INFO ------------------
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


# ------------------ 🛒 ORDER ------------------
# orders/models.py
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    delivery_person = models.ForeignKey(
        DeliveryPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_orders'
    )
    
    # NEW FIELDS
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

# ------------------ 🧾 ORDER ITEMS ------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    @property
    def subtotal(self):
        return self.price * self.quantity
# ------------------ 🎁 OFFERS ------------------
class Offer(models.Model):
    DISCOUNT_TYPE = (
        ('percent', 'Percentage'),
        ('flat', 'Flat Amount'),
    )

    name = models.CharField(max_length=200)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
