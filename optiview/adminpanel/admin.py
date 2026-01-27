from django.contrib import admin

# Register your models here.
from .models import*
# from .models import Product, Category

# Register your models here.
admin.site.register(Product)
admin.site.register(Lens)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(CompanyInfo)
admin.site.register(Category)
