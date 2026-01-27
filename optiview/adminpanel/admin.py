from django.contrib import admin
from .models import *


 # Must be an actual model field, not a property



admin.site.register(Product,)
admin.site.register(Lens)
admin.site.register(Order)
admin.site.register(Notification)
admin.site.register(CompanyInfo)
admin.site.register(Category)

