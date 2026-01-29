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
