from django.contrib import admin
from .models import*

@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'joining_date')
