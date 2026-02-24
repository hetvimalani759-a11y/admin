from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [

    # ================= AUTH =================
     path("users/", views.user_list, name="user_list"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ================= DASHBOARD =================
    path("", views.dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # ================= CATEGORY =================
    path("category/add/", views.add_category, name="add_category"),
     path("category/edit/<int:id>/", views.edit_category, name="edit_category"),
    path("category/delete/<int:id>/", views.delete_category, name="delete_category"),

    # ================= SUBCATEGORY =================
    path("subcategory/add/", views.add_subcategory, name="add_subcategory"),
    path("subcategory/edit/<int:id>/", views.edit_subcategory, name="edit_subcategory"),
    path("subcategory/delete/<int:id>/", views.delete_subcategory, name="delete_subcategory"),
    path("ajax/subcategories/<int:category_id>/", views.get_subcategories, name="get_subcategories"),

    # ================= PRODUCTS =================
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path("products/delete/<int:id>/", views.delete_product, name="delete_product"),

    # LENS
    path("lenses/", views.lens_list, name="lens_list"),

    # ================= ORDERS =================
    path("orders/", views.order_list, name="order_list"),
    path("assign-order-ajax/", views.assign_order_ajax, name="assign_order_ajax"),
      
     

    # ================= DELIVERY PERSON =================
    path("delivery-persons/", views.delivery_person_list, name="delivery_person_list"),
    path("delivery-persons/add/", views.add_delivery_person, name="add_delivery_person"),

    # ================= OFFERS =================
    path("offers/", views.offer_list, name="offer_list"),
    path("offers/create/", views.create_offer, name="create_offer"),
      path("reset-password/<int:id>/", views.reset_password, name="reset_password"),

    # ================= NOTIFICATIONS =================
    path(
        "notifications/mark-read/<int:notification_id>/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),
     path("notifications/", views.notifications, name="notifications"),
     path("revenue/", views.revenue_dashboard, name="revenue_dashboard"),
     path("low-stock/", views.low_stock_products, name="low_stock_products"),
     path("company/create/", views.company_create, name="company_create"),
    path("notifications/add/", views.add_notification, name="add_notification"),
    
]
