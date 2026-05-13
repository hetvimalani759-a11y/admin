from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "adminpanel"

urlpatterns = [
    # Auth URLs
    # path('admin-panel/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('admin-panel/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/add/', views.add_dashboard_image, name='add_dashboard_image'),
    path("dashboard-image/edit/<int:id>/", views.edit_dashboard_image, name="edit_dashboard_image"),
    path("dashboard-image/delete/<int:id>/", views.delete_dashboard_image, name="delete_dashboard_image"),
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/add/', views.add_notification, name='add_notification'),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
    path('toggle-user/<int:id>/', views.toggle_user, name='toggle_user'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),
    # Category URLs
    path("category/add/", views.add_category, name="add_category"),
    path('category/edit/<int:id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:id>/', views.delete_category, name='delete_category'),

    # Subcategory URLs
    path('subcategory/edit/<int:id>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    path("subcategory/add/", views.add_subcategory, name="add_subcategory"),
    path('subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('admin-forgot-password/', views.admin_forgot_password, name='forgot_password'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('admin-verify-otp/', views.admin_verify_otp, name='verify_otp'),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path("ajax/subcategories/<int:category_id>/", views.get_subcategories, name="get_subcategories"),
    path('products/add/', views.add_product, name='add_product'),
    path("products/edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('frame-type/', views.frame_type_list, name='frame_type_list'),
    path('add-frame-type/', views.add_frame_type, name='add_frame_type'),
    path("frame-type/edit/<int:pk>/", views.edit_frame_type, name="edit_frame_type"),
    path("frame-type/delete/<int:pk>/", views.delete_frame_type, name="delete_frame_type"),
    path("frame-shape/", views.frame_shape_list, name="frame_shape_list"),
    path("frame-shape/add/", views.add_frame_shape, name="add_frame_shape"),
    path('frame-shape/edit/<int:pk>/', views.edit_frame_shape, name='edit_frame_shape'),
    path('frame-shape/delete/<int:pk>/', views.delete_frame_shape, name='delete_frame_shape'),

    # Other admin-panel URLs
    path("lenses/", views.lens_list, name="lens_list"),
    path("lenses/add/", views.add_lens, name="add_lens"),
    path("lenses/edit/<int:pk>/", views.edit_lens, name="edit_lens"),
    path("lenses/delete/<int:pk>/", views.delete_lens, name="delete_lens"),

    # path('orders/', views.order_list, name='order_list'),
    path('users/', views.user_list, name='user_list'),
    path('low_stock/', views.low_stock_products, name="low_stock_products"),
    path("revenue/", views.revenue_dashboard, name="revenue_dashboard"),
    path("company/add/", views.company_create, name="company_create"),
    path("company/edit/", views.company_update, name="company_update"),
    path('offers/create/', views.create_offer, name='create_offer'),
    path('offers/', views.offer_list, name='offer_list'),
    path('offers/edit/<int:pk>/', views.edit_offer, name='edit_offer'),
    path('offers/delete/<int:pk>/', views.delete_offer, name='delete_offer'),

    # Delivery-person URLs
    path('delivery-persons/', views.delivery_person_list, name='delivery_person_list'),
    path("delivery-persons/add/", views.add_delivery_person, name="delivery_person_add"),
    path(
    "orders/<int:order_id>/assign-delivery/",
    views.assign_delivery,
    name="assign_delivery"
    ),
    path('orders/',views.orders_list,name='orders_list'),

    # Order status updates
    path("orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),
    path("stock-report/", views.stock_report, name="stock_report"),
    path("profit-report/", views.profit_report, name="profit_report"),
    path("purchase/invoice/<int:id>/", views.purchase_invoice, name="purchase_invoice"),
    path('dealers/', views.dealer_list, name='dealer_list'),
    path('dealer/add/', views.add_dealer, name='add_dealer'),
    path('dealers/edit/<int:dealer_id>/', views.edit_dealer, name='edit_dealer'),
    path('dealers/delete/<int:dealer_id>/', views.delete_dealer, name='delete_dealer'),
   
    path('check-product-name/', views.check_product_name, name='check_product_name'),
    # path('orders/update/<int:order_id>/',views.update_order_status,name='update_order_status'),
    # Order status updates
    # path('purchase/add/', views.add_purchase_page, name='add_purchase_page'),
    path("refund-complete/<int:item_id>/",views.complete_refund, name="complete_refund"),
    path("approve-return/<int:item_id>/", views.approve_return, name="approve_return"),
    path("return-reject/<int:item_id>/", views.reject_return, name="return_reject"),
    path("complaint/add/<int:item_id>/",views.add_complaint,name="add_complaint"),
    path("complaints/", views.complaints_list,name="complaints_list"),
    path("complaint/resolve/<int:id>/",views.resolve_complaint,name="resolve_complaint"),
    path("complaint/reject/<int:id>/",views.reject_complaint, name="reject_complaint"),
    path('complaints/<int:id>/', views.complaint_detail, name='complaint_detail'),
    path("reviews/", views.review_list, name="review_list"),
    # path('reports/', views.report_view, name='report_view'),
    # path("profile/", views.admin_profile, name="profile"),
    # path("profile/edit/", views.edit_profile, name="edit_profile"),
    # path("profile/change-password/", views.change_password, name="change_password"),
    path("purchase/", views.purchase_list, name="purchase_list"),
    path("purchase/add/", views.add_purchase, name="add_purchase"),
    path("purchase/edit/<int:id>/", views.edit_purchase, name="edit_purchase"),
    path('purchase-returns/', views.purchase_return_list, name='purchase_return_list'),
    path('purchase-return/add/', views.add_purchase_return, name='add_purchase_return'),
    path("purchase/delete/<int:id>/", views.delete_purchase, name="delete_purchase"),
    path('add-brand/', views.add_brand_page, name='add_brand'),
    path('add-brand/edit/<int:id>/', views.edit_brand, name='edit_brand'),  # <-- add this
    path('add-brand/delete/<int:id>/', views.delete_brand, name='delete_brand'),  # if using delete
    path("add-material/", views.add_material, name="add_material"),
    path('edit-material/<int:pk>/', views.edit_material, name='edit_material'),
    path('delete-material/<int:pk>/', views.delete_material, name='delete_material'),
    path('add-color/', views.add_color_page, name='add_color_page'),
    path("color/edit/<int:pk>/", views.edit_color, name="edit_color"),
    path("color/delete/<int:pk>/", views.delete_color, name="delete_color"),
    path('reports/', views.reports, name='reports')

    # Other URLs if needed...

    # path("refund-complete/<int:item_id>/",views.complete_refund, name="complete_refund"),
    #  path("approve-return/<int:item_id>/", views.approve_return, name="approve_return"),
    # path("return-reject/<int:item_id>/", views.reject_return, name="return_reject"),
    # path("complaint/add/<int:item_id>/",views.add_complaint,name="add_complaint"),
    # path("complaints/", views.complaints_list,name="complaints_list"),
    # path("complaint/resolve/<int:id>/",views.resolve_complaint,name="resolve_complaint"),
    # path("complaint/reject/<int:id>/",views.reject_complaint, name="reject_complaint"),
    # path('complaints/<int:id>/', views.complaint_detail, name='complaint_detail'),
    # path("reviews/", views.review_list, name="review_list"),

    # Other URLs if needed...
]
