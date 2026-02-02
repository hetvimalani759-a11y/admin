from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),

    # Cart
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/increase/<int:item_id>/", views.increase_qty, name="increase_qty"),
    path("cart/decrease/<int:item_id>/", views.decrease_qty, name="decrease_qty"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/count/", views.cart_count, name="cart_count"),

    # Wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/remove/<int:item_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),

    # Auth & Pages
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # Notifications
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/read/<int:pk>/", views.mark_notification_read, name="mark_notification_read"),

    path("checkout/", views.checkout, name="checkout"),
    path("order-success/", views.order_success, name="order_success"),
    path("place-order/", views.place_order, name="place_order"),
    path('orders/history/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail')


]
