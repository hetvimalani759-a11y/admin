from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Product







class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    def total_price(self):
        return self.product.price * self.quantity
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')   # 🔥 THIS LINE ADD

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"



# class Wishlist(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="wishlist_items"   # 👈 aa add karo
#     )

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name}"
