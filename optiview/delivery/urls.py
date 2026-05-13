from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = "delivery"

urlpatterns = [

    path('', RedirectView.as_view(pattern_name='delivery:delivery_login', permanent=False)),

    # Authentication
    path('login/', views.delivery_login, name='delivery_login'),
    path('logout/', views.delivery_logout, name='delivery_logout'),


    # Dashboard
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),

    # Orders
    path('my-orders/', views.my_orders, name='my_orders'),

    # ✅ ONLY ONE update-orders path
    path('update-orders/', views.update_status, name='update_status'),

    # Item status update
    path('update-item/<int:item_id>/', views.update_item_status, name='update_item_status'),

    # Profile
    path('profile/', views.delivery_profile, name='delivery_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("change-password/", views.delivery_change_password, name="delivery_change_password"),

    # Filter pages
    path("accepted-orders/", views.accepted_orders, name="accepted_orders"),
    path("rejected-orders/", views.rejected_orders, name="rejected_orders"),
    path("cancelled-orders/", views.cancelled_orders, name="cancelled_orders"),
    path("assigned-orders/", views.assigned_orders, name="assigned_orders"),
    path("pending-orders/", views.pending_orders, name="pending_orders"),
    path("out-of-delivery-orders/", views.out_of_delivery_orders, name="out_of_delivery_orders"),
    path("delivered-orders/", views.delivered_orders, name="delivered_orders"),
    path("order-action/<int:order_id>/",views.accept_reject_order,name="accept_reject_order") ,
    path('delivery-forgot-password/', views.delivery_forgot_password, name='delivery_forgot_password'),
    path('delivery-verify-otp/', views.delivery_verify_otp, name='delivery_verify_otp'), 

]