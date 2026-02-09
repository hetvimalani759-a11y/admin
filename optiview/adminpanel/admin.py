from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',              # this replaces customer_name
        'delivery_person',
        'total_amount',
        'status',
        'created_at',
    )
    list_filter = ('status', 'delivery_person')
    list_editable = ('delivery_person','status')
    search_fields = ('user__username',)  # search by username
from django.contrib.auth.models import User
from .models import *


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("title", "message", "user__username")
    actions = ["send_to_all_users"]

    def send_to_all_users(self, request, queryset):
        users = User.objects.all()
        for notif in queryset:
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=notif.title,
                    message=notif.message
                )
        self.message_user(request, "Notification sent to all users successfully.")

    send_to_all_users.short_description = "Send selected notification(s) to ALL users"



@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'discount_type')

admin.site.register(Product)
admin.site.register(Lens)
# admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CompanyInfo)
admin.site.register(Category)
