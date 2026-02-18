from .models import Notification

# def send_notification(user, title, message):
#     Notification.objects.create(user=user, title=title, message=message)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_delivery(user):
    return user.is_authenticated and user.is_staff and hasattr(user, "deliveryperson")

def is_customer(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser
