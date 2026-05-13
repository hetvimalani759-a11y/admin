from django.urls import path
from . import views

urlpatterns = [
    path('assign/<int:order_id>/', views.assign_order, name='assign_order'),
]