from django.urls import path
from django.views.generic import RedirectView
from . import views


app_name = "delivery"


urlpatterns = [

    # =========================
    # DEFAULT REDIRECT
    # =========================
    path(
        "",
        RedirectView.as_view(pattern_name="delivery:delivery_login", permanent=False),
        name="delivery_home_redirect"
    ),

    # =========================
    # AUTH
    # =========================
    path("login/", views.delivery_login, name="delivery_login"),
    path("logout/", views.delivery_logout, name="delivery_logout"),

    # =========================
    # PASSWORD
    # =========================
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"),

    # =========================
    # DASHBOARD & ORDERS
    # =========================
    path("dashboard/", views.delivery_dashboard, name="delivery_dashboard"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("orders/accept/<int:order_id>/", views.accept_order, name="accept_order"),
     path("orders/reject/<int:order_id>/", views.reject_order, name="reject_order"),

    # =========================
    # PROFILE
    # =========================
    path("profile/", views.delivery_profile, name="delivery_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # =========================
    # ADMIN SIDE – DELIVERY MANAGEMENT
    # =========================
    path("delivery-persons/", views.delivery_person_list, name="delivery_person_list"),
   # path("delivery-action/<int:order_id>/<str:action>/", views.delivery_action, name="delivery_action"),
    path(
        "order/<int:order_id>/<str:action>/",
        views.delivery_action,
        name="delivery_action",
    ),
]
