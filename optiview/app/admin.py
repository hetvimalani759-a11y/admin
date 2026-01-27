from django.contrib import admin
from django.core.mail import send_mail
from .models import Product, Notification
from django.contrib.auth.models import User

def apply_discount(modeladmin, request, queryset):
    discount_percent = 10  # Example: 10%
    for product in queryset:
        product.discount_price = product.price * (1 - discount_percent / 100)
        product.save()
    
    # # Notify users via email
    # for user in User.objects.all():
    #     send_mail(
    #         subject="Discount Alert!",
    #         message=f"Hello {user.username}, we have {discount_percent}% off on all products!",
    #         from_email="asitamalani@gmail.com",
    #         recipient_list=[user.email],
    #     )
    
    # Optional: Notify users in DB
    for user in User.objects.all():
        Notification.objects.create(
            user=user,
            message=f"{discount_percent}% discount on all products!"
        )
    
    modeladmin.message_user(request, f"{queryset.count()} products discounted by {discount_percent}%")

apply_discount.short_description = "Apply discount to selected products"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price')
    actions = [apply_discount]
