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
    path("users/", views.user_list, name="user_list"),
    path("get-subcategories/<int:category_id>/",views.get_subcategories, name="get_subcategories"),
    path("category/add/", views.add_category, name="add_category"),
    path('category/edit/<int:id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('subcategory/edit/<int:id>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    path("subcategory/add/", views.add_subcategory, name="add_subcategory"),
    path('products/', views.product_list, name='product_list'),
    path("ajax/subcategories/<int:category_id>/", views.get_subcategories, name="get_subcategories"),
    path('products/add/', views.add_product, name='add_product'),
    path("products/edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('lenses/', views.lens_list, name='lens_list'),
    path('orders/', views.order_list, name='order_list'),
    path('low_stock/',views.low_stock_products, name="low_stock_products"),
    path("revenue/", views.revenue_dashboard, name="revenue_dashboard"),
   # path('add-order/',views.add_order, name='add_order'),
    path("company/add/", views.company_create, name="company_create"),
    path("company/edit/", views.company_update, name="company_update"),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
    path('assign-order/', views.assign_order, name='assign_order'),
    path('delivery-persons/', views.delivery_person_list, name='delivery_person_list'),
    
    path('offers/create/', views.create_offer, name='create_offer'),
    path('offers/', views.offer_list, name='offer_list'),
    path('offers/edit/<int:pk>/', views.edit_offer, name='edit_offer'),
    path('offers/delete/<int:pk>/', views.delete_offer, name='delete_offer'),
    path("orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),




    path('orders/update/<int:order_id>/',views.update_order_status,name='update_order_status')
]
