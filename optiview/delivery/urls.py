from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = "delivery"

urlpatterns = [
    # Redirect /delivery/ → /delivery/login/
    path('', RedirectView.as_view(pattern_name='delivery:delivery_login', permanent=False)),

    # Authentication
    path('login/', views.delivery_login, name='delivery_login'),
    path('logout/', views.delivery_logout, name='delivery_logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),

    # Dashboard & Orders
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Profile
    path('profile/', views.delivery_profile, name='delivery_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Admin — Delivery Person Management
    # path('delivery-persons/', views.delivery_person_list, name='delivery_person_list'),
    # path('delivery-persons/add/', views.add_delivery_person, name='add_delivery_person'),
]
