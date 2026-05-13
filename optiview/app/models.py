from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from adminpanel.models import Product,ProductVariant

User = get_user_model()
class PincodeMapping(models.Model):
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('pincode', 'area')
    def __str__(self):
        return f"{self.pincode} - {self.area}, {self.city}"
class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)  # optional storage

    # ✅ Auto-generate pincode
    # NEW CODE: use PincodeMapping
    def save(self, *args, **kwargs):
        if self.city and self.area:
            mapping = PincodeMapping.objects.filter(city=self.city, area=self.area).first()
            self.pincode = mapping.pincode if mapping else ""
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username
from adminpanel.models import Product, ProductVariant,Lens

# models.py

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)
    
    # ✅ LENS INFO
    lens = models.ForeignKey(
    Lens,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
    left_eye_power = models.CharField(max_length=10, blank=True, null=True)
    right_eye_power = models.CharField(max_length=10, blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
    'user',
    'product',
    'variant',
    'lens',
    'left_eye_power',
    'right_eye_power'
)
        ordering = ['-added_at']

    def clean(self):
        if self.variant and self.quantity > self.variant.stock:
            raise ValidationError("Quantity exceeds available stock.")

    from decimal import Decimal

    @property
    def unit_price(self):
        price = self.product.get_final_price() or Decimal("0.00")

        price = Decimal(price)

        if self.lens:
            price += Decimal(self.lens.additional_price)

        return price
    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        info = f"{self.user.username} - {self.product.name}"

        if self.variant:
            info += f" ({self.variant.color.name})"

        if self.lens:
            info += f" [{self.lens.name}"

        if self.left_eye_power or self.right_eye_power:
            info += f" L:{self.left_eye_power} R:{self.right_eye_power}"

        info += "]"

        return info
# ==============================
# WISHLIST
# ==============================

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ==============================
# SAVE FOR LATER
# ==============================

# class SaveForLater(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'product')

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name}"


# ==============================
# COUPON USAGE TRACKING
# ==============================

# class CouponUsage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="used_coupons")
#     coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

#     used_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'coupon')

#     def __str__(self):
#         return f"{self.user.username} used {self.coupon.code}"