from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('shop/', views.shop, name='shop'),
    path('shop/', views.shop),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/read/<int:id>/", views.mark_read, name="mark_read"),
    path('product/<int:id>/', views.product_detail),
    path('products/', views.product_list, name='product_list'),
    path('lenses/', views.lens_list, name='lens_list'),

]
