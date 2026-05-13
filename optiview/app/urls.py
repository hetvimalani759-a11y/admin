from django.urls import path
from . import views
app_name = "app" 
urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path('categories/', views.categories_view, name='categories'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),
    # path('shop/category/<int:category_id>/', views.shop_by_category, name='shop_by_category'),


    # Cart
     path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/increase/<int:item_id>/", views.increase_qty, name="increase_qty"),
    path("cart/decrease/<int:item_id>/", views.decrease_qty, name="decrease_qty"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/count/", views.cart_count, name="cart_count"),
    path("virtualtryon/<int:product_id>/",
     views.virtualtryon,
     name="virtualtryon"),
    path("virtual_tryon/", views.virtual_tryon, name="virtual_tryon"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("profile/", views.profile, name="profile"),
    path("change-password/", views.change_password, name="change_password"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'), 
    path('get-address/<str:pincode>/', views.get_full_address_by_pincode, name='get_address'),
    # urls.py

    path('api/get-location/<str:pincode>/', views.get_location_by_pincode, name='get_location_by_pincode'),
    path('api/get-pincode/', views.get_pincode, name='get_pincode'),
    path('add-feedback/<int:item_id>/', views.add_feedback, name='add_feedback'),
    # Wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/remove/<int:item_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),

    # Auth & Pages
   path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path("logout/", views.customer_logout, name="logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("create-order/", views.create_order, name="create_order"),
    path("api/get-cities/", views.get_cities, name="get_cities"),
    # path('notifications/', views.notifications_api, name='notifications_api'),
    path("order-invoice/<int:order_id>/", views.order_invoice, name="order_invoice"),
        
    # Notifications
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/read/<int:pk>/", views.mark_notification_read, name="mark_notification_read"),

    path("checkout/", views.checkout, name="checkout"),
    path("order-success/", views.order_success, name="order_success"),
    # path("place-order/", views.place_order, name="place_order"),
    path('orders/history/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path(
    "cancel-item/<int:item_id>/",
    views.cancel_order_item,
    name="cancel_order_item"
),
path(
    "return/<int:item_id>/",
    views.return_request,
    name="return_request"
),

]
