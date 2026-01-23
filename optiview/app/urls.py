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
    path('product/<int:id>/', views.product_detail),
    path('products/', views.product_list, name='product_list'),
    path('lenses/', views.lens_list, name='lens_list'),

]
