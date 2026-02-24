from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
     Order,
    Notification,
    Offer,
    Product,
    Lens,
    OrderItem,
    CompanyInfo,
    Category
)


# =====================================
# 📦 ORDER ADMIN
# =====================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "delivery_person")
    ordering = ("-id",)
    list_filter = ("status", "delivery_person")
    list_editable = ("delivery_person", "status")
    search_fields = ("user__username",)
 


# =====================================
# 🔔 NOTIFICATION ADMIN
# =====================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_read", "created_at")
    ordering = ("-created_at",)

    search_fields = ("title", "message", "receiver__username", "sender__username")
    actions = ["send_to_all_users"]

    def send_to_all_users(self, request, queryset):
        users = User.objects.all()

        for notif in queryset:
            for user in users:
                Notification.objects.create(
                    sender=request.user,
                    receiver=user,
                    order=notif.order,   # ✅ FIXED (important)
                    title=notif.title,
                    message=notif.message,
                )

        self.message_user(request, "Notification sent to all users successfully.")

    send_to_all_users.short_description = "Send selected notification(s) to ALL users"


# =====================================
# 🎁 OFFER ADMIN
# =====================================
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_type",
        "discount_value",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("is_active", "discount_type")
    search_fields = ("name",)


# =====================================
# 📌 SIMPLE REGISTRATIONS
# =====================================
admin.site.register(Product)
admin.site.register(Lens)
admin.site.register(OrderItem)
admin.site.register(CompanyInfo)
admin.site.register(Category)
