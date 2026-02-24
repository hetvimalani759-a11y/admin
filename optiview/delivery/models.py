from django.db import models
from django.contrib.auth.models import User


# =====================================
# 🚚 DELIVERY PERSON
# =====================================
class DeliveryPerson(models.Model):

    profile_image = models.ImageField(
        upload_to="delivery/profile/",
        default="delivery/default-user.png",
        blank=True
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_profile"
    )

    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-joining_date"]

    def __str__(self):
        return self.user.username


# =====================================
# 🔔 NOTIFICATION
# =====================================
class Notification(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_delivery_notifications"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_delivery_notifications"
    )
    order = models.ForeignKey(
    "orders.Order",
    on_delete=models.CASCADE,
    null=True,
    blank=True
)


    # ✅ Added title (because your views use it)
    title = models.CharField(max_length=100)

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} | Order #{self.order.id}"
