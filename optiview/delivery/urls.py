# urls.py
from django.urls import path
from . import views
from django.views.generic import RedirectView




urlpatterns = [
    path('', RedirectView.as_view(pattern_name='delivery_login', permanent=False)),  # redirect /delivery -> /delivery/login/
    path('login/', views.delivery_login, name='delivery_login'),
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('logout/', views.delivery_logout, name='delivery_logout'),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('profile/', views.delivery_profile, name='delivery_profile'),
     path('profile/edit/', views.edit_profile, name='edit_profile'),
]
