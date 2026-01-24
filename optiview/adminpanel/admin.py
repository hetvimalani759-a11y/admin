from django.contrib import admin

# Register your models here.
from .models import*

# Register your models here.
admin.site.register(Product)
admin.site.register(Lens)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(CompanyInfo)
