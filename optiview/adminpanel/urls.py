from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin-panel/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin-panel/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

app_name = "adminpanel"   # ✅ This is mandatory

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/add/', views.add_notification, name='add_notification'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('lenses/', views.lens_list, name='lens_list'),
    path('orders/', views.order_list, name='order_list'),
    path('add-order/',views.add_order, name='add_order'),
    path('company/update/',views.update_company_info,name='update_company_info'),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
    # path('orders/update/<int:order_id>/',views.update_order_status,name='update_order_status')
]
