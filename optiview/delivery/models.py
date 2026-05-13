from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ==============================
# DELIVERY PERSON
# ==============================
class DeliveryPerson(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
           related_name="delivery_profile"
    
    )

    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    joining_date = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.user.username


class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message