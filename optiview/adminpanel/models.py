from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from decimal import Decimal

User = get_user_model()


# ==============================
# CATEGORY
# ==============================

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==============================
# SUBCATEGORY
# ==============================

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ["name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# ==============================
# BRAND
# ==============================

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ==============================
# COLOR
# ==============================

class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return self.name


# ==============================
# PRODUCT
# ==============================

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=200)
    description = models.TextField()
    stock = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    gender = models.CharField(
        max_length=20,
        choices=[('Men','Men'),('Women','Women'),('Unisex','Unisex')]
    )

    frame_type = models.CharField(
        max_length=20,
        choices=[('Full Rim','Full Rim'),('Half Rim','Half Rim'),('Rimless','Rimless')]
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    # ✅ OFFER LOGIC INSIDE CLASS

    def get_best_offer(self):
        today = timezone.now().date()
        base_price = self.price

        offers = Offer.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).filter(
            Q(product=self) | Q(category=self.category)
        )

        best_offer = None
        lowest_price = base_price

        for offer in offers:

            if offer.discount_type == "percent":
                discount_amount = (base_price * offer.discount_value) / Decimal("100")
                new_price = base_price - discount_amount

            elif offer.discount_type == "flat":
                new_price = base_price - offer.discount_value

            else:
                continue

            if new_price < 0:
                new_price = Decimal("0")

            if new_price < lowest_price:
                lowest_price = new_price
                best_offer = offer

        return best_offer

    def get_final_price(self):
        offer = self.get_best_offer()

        if not offer:
            return self.price

        base_price = self.price

        if offer.discount_type == "percent":
            discount = (base_price * offer.discount_value) / Decimal("100")
        elif offer.discount_type == "flat":
            discount = offer.discount_value
        else:
            return base_price

        final_price = base_price - discount

        return max(final_price, Decimal("0"))

# ==============================
# PRODUCT VARIANT
# ==============================

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.color.name}"


class ProductVariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/variants/")

    def __str__(self):
        return f"{self.variant} Image"


# ==============================
# LENS
# ==============================

class Lens(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    additional_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==============================
# OFFER
# ==============================

class Offer(models.Model):

    DISCOUNT_TYPE = [
        ('percent', 'Percentage'),
        ('flat', 'Flat Amount'),
    ]

    name = models.CharField(max_length=200)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    def clean(self):
        if not self.product and not self.category:
            raise ValidationError("Offer must apply to product or category")

    def __str__(self):
        return self.name


# ==============================
# COUPON
# ==============================

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField()

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date

    def __str__(self):
        return self.code


# ==============================
# ORDER
# ==============================

class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Placed', 'Placed'),
        ('Shipped', 'Shipped'),
        ('Assigned', 'Assigned'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    order_number = models.CharField(max_length=20, unique=True, blank=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=50)
    payment_status = models.BooleanField(default=False)
    delivery_person = models.ForeignKey(
    "DeliveryPerson",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders"
)


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"OPT{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# ==============================
# ORDER ITEM
# ==============================

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    lens = models.ForeignKey(Lens, on_delete=models.SET_NULL, null=True, blank=True)

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

# ==============================
# PURCHASE (STOCK ENTRY)
# ==============================

class Purchase(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchases'
    )

    variant = models.ForeignKey(
        'ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    dealer_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    purchase_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 Auto increase stock
        if self.variant:
            self.variant.stock += self.quantity
            self.variant.save()
        else:
            self.product.stock += self.quantity
            self.product.save()

    def __str__(self):
        variant_info = f" - {self.variant.color.name}" if self.variant else ""
        return f"{self.product.name}{variant_info} ({self.quantity})"

# ==============================
# REVIEW
# ==============================

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"


# ==============================
# NOTIFICATION
# ==============================

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ==============================
# DELIVERY PERSON
# ==============================

class DeliveryPerson(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==============================
# COMPANY INFO
# ==============================

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to="company/")

    def __str__(self):
        return self.name


# ==============================
# DASHBOARD IMAGE
# ==============================

class DashboardImage(models.Model):
    image = models.ImageField(upload_to="dashboard/")
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title if self.title else "Dashboard Image"
