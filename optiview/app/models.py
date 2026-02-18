from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from adminpanel.models import Product

User = get_user_model()


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

    # ✅ STORE COLOR
    color = models.CharField(max_length=50)

    quantity = models.PositiveIntegerField(default=1)
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ✅ Important: allow same product but different color
        unique_together = ('user', 'product', 'color')
        ordering = ['-added_at']

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError("Quantity exceeds available stock.")

    # ✅ Unit price (after offer)
    @property
    def unit_price(self):
        return self.product.get_final_price()

    # ✅ Total price (after offer × quantity)
    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.color})"


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
