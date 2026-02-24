
from django.urls import path
from . import views
urlpatterns = [
path('assign-order/<int:order_id>/', views.assign_order, name='assign_order'),
]