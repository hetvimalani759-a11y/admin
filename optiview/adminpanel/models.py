from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from decimal import Decimal
import webcolors
# from adminpanel.models import FrameShape,FrameType

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
    allow_lens = models.BooleanField(
        default=False,
        help_text="Enable lens selection for this subcategory (e.g., Eyeglasses)"
    )

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
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=7, blank=True)

    def save(self, *args, **kwargs):
        # If code empty but name given → auto convert
        if not self.code and self.name:
            try:
                self.code = webcolors.name_to_hex(self.name.lower())
            except ValueError:
                raise ValidationError("Invalid color name")

        # If user enters name in code field
        elif self.code and not self.code.startswith('#'):
            try:
                self.code = webcolors.name_to_hex(self.code.lower())
            except ValueError:
                raise ValidationError("Enter valid color name or hex code")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==============================
# PRODUCT
# ==============================
class Material(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class FrameType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class FrameShape(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=200)
    description = models.TextField()
    material = models.ForeignKey(
    Material,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    
    
    frame_type = models.ForeignKey(FrameType, on_delete=models.SET_NULL,blank=True, null=True)
    frame_shape = models.ForeignKey(FrameShape, on_delete=models.SET_NULL, null=True, blank=True)
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
    
    # def has_stock(self):
    #     return self.variants.filter(stock__gt=0).exists()
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
    power_required = models.BooleanField(default=True)
    # False for Normal Lens


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
# ORDER
# ==============================

class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
        ("out_for_delivery", "Out For Delivery"),
        ("delivered", "Delivered"),
        ("partially_delivered", "Partially Delivered"), 
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Customer Info
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    payment_method = models.CharField(max_length=50)
    payment_status = models.BooleanField(default=False)

    delivery_person = models.ForeignKey(
        "delivery.DeliveryPerson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    last_rejected_by = models.ForeignKey(
        "delivery.DeliveryPerson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_orders"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    # 🔥 Auto generate order number
    def save(self, *args, **kwargs):

        if not self.order_number:
            self.order_number = f"OPT{timezone.now().strftime('%Y%m%d%H%M%S')}"

        if self.delivery_person and self.status == "pending":
            self.status = "assigned"

        super().save(*args, **kwargs)

    # 🔥 Calculate total from items
    @property
    def get_total_amount(self):
        return sum(item.total_price for item in self.items.all())

    # 🔥 AUTO UPDATE ORDER STATUS BASED ON ITEMS
    def update_order_status(self):

     items = self.items.all()

     if not items.exists():
        return

     total = items.count()

     delivered = items.filter(status="delivered").count()
     cancelled = items.filter(status="cancelled").count()
     out = items.filter(status="out_for_delivery").count()
     accepted = items.filter(status="accepted").count()

    # 🔴 All cancelled
     if cancelled == total:
        self.status = "cancelled"

    # 🟢 All delivered
     elif delivered == total:
        self.status = "delivered"

    # 🟡 Mix delivered + cancelled
     elif delivered > 0 and cancelled > 0:
        self.status = "partially_delivered"

    # 🚚 Out for delivery
     elif out > 0:
        self.status = "out_for_delivery"

    # 📦 Accepted
     elif accepted > 0:
        self.status = "accepted"

     else:
        self.status = "assigned"

     self.save(update_fields=["status"])
# ==============================
# ORDER ITEM

class OrderItem(models.Model):

    ITEM_STATUS = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("out_for_delivery", "Out For Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    RETURN_STATUS = [
        ('none','None'),
        ('requested','Return Requested'),
        ('approved','Return Approved'),
        ('rejected','Return Rejected'),
        ('completed','Return Completed'),
    ]

    REFUND_STATUS = [
        ('none', 'None'),
        ('initiated', 'Refund Initiated'),
        ('completed', 'Refund Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    lens = models.ForeignKey(Lens, on_delete=models.SET_NULL, null=True, blank=True)
    lens_type = models.CharField(max_length=20, blank=True, null=True)
    left_eye_power = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    right_eye_power = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=ITEM_STATUS,
        default="pending"
    )

    # 🔁 RETURN
    return_status = models.CharField(
        max_length=30,
        choices=RETURN_STATUS,
        default="none"
    )

    return_reason = models.TextField(blank=True, null=True)

    # 💰 REFUND
    refund_status = models.CharField(
        max_length=30,
        choices=REFUND_STATUS,
        default="none"
    )

    @property
    def unit_price(self):
        return self.price()

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
# ==============================
# PURCHASE (STOCK ENTRY)
# ==============================
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at
    

class Dealer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=100)
    purchase_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.bill_number} - {self.dealer.name}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("ProductVariant", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.cost_price
    
from django.core.exceptions import ValidationError

class PurchaseReturn(models.Model):
    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.CASCADE,
        related_name='returns'
    )
    return_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        variant = self.purchase_item.variant

        if self.quantity > variant.stock:
            raise ValidationError("Return quantity cannot exceed available stock.")

        # 🔽 Reduce stock because items are returned to dealer
        variant.stock -= self.quantity
        variant.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return: {self.purchase_item.variant} ({self.quantity})"



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
# class DeliveryPerson(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=15)
#     email = models.EmailField()
#     joining_date = models.DateField(null=True, blank=True) 
#     def __str__(self):
#         return self.user.username

# ==============================
# COMPANY INFO
# ==============================

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to="company/")

    def __str__(self):
        return self.name


# ==============================
# DASHBOARD IMAGE
# ==============================

class DashboardImage(models.Model):
    image = models.ImageField(upload_to="dashboard/")
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, null=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title if self.title else "Dashboard Image"


class Complaint(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    )

    order_item = models.ForeignKey(
        "adminpanel.OrderItem",
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    reason = models.CharField(max_length=200)

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.id}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"
    

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="admin_profile"   # 👈 VERY IMPORTANT
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return self.user.username
    
from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='admin_profile/', blank=True, null=True)

    def __str__(self):
        return self.user.username