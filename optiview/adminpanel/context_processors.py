from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        return {
            "notification_count": Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {"notification_count": 0}

from .models import ProductVariant

LOW_STOCK_THRESHOLD = 50

def low_stock_alert(request):
    if not request.path.startswith("/admin-panel/"):
        return {}

    low_variants = ProductVariant.objects.filter(
        stock__lte=LOW_STOCK_THRESHOLD
    ).select_related("product", "color")

    return {
        "low_stock_variants": low_variants,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
    }