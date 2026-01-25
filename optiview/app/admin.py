from django.contrib import admin
from django.contrib.auth.models import User
from .models import Notification


@admin.action(description="Send this notification to ALL users")
def send_to_all_users(modeladmin, request, queryset):
    users = User.objects.all()

    for obj in queryset:
        for user in users:
            # create separate notification for each user
            Notification.objects.create(
                user=user,
                title=obj.title,
                message=obj.message
            )

        # delete admin template notification (optional but recommended)
        obj.delete()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "is_read")
    actions = [send_to_all_users]