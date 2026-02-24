from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from orders.models import Order
from delivery.models import DeliveryPerson


from .models import (
    Product, Category, SubCategory, Offer, Lens, CompanyInfo,
    Order, OrderItem, DeliveryPerson, Notification
)

LOW_STOCK_THRESHOLD = 50


# ================= AUTH =================

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user and user.is_staff:
            login(request, user)
            messages.success(request, "Welcome Admin")
            return redirect("adminpanel:dashboard")
        messages.error(request, "Invalid credentials")
    return render(request, "admin/login.html")


@login_required(login_url="adminpanel:login")
def logout_view(request):
    logout(request)
    return redirect("adminpanel:login")


# ================= DASHBOARD =================

@login_required(login_url="adminpanel:login")
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_lenses = Lens.objects.count()
    total_users = User.objects.count()

    total_revenue = Order.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    monthly_revenue = (
        Order.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    )

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_lenses": total_lenses,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "latest_products": Product.objects.order_by("-created_at")[:5],
        "company": CompanyInfo.objects.first(),
        "monthly_revenue": monthly_revenue,
        "revenue_months": [r["month"].strftime("%b %Y") for r in monthly_revenue],
        "revenue_values": [r["total"] for r in monthly_revenue],
        "notifications": notifications,
        "low_stock": Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD).count(),
    }

    return render(request, "admin/dashboard.html", context)


# ================= CATEGORY =================

@login_required
def add_category(request):
    categories = Category.objects.all().order_by("-id")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, "Category added successfully")
        return redirect("adminpanel:add_category")
    return render(request, "admin/add_category.html", {"categories": categories})


# ================= PRODUCT =================

@login_required
def product_list(request):
    search = request.GET.get("search", "")
    products = Product.objects.all()
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__icontains=search)
        )
    return render(request, "admin/product_list.html", {
        "products": products,
        "search": search
    })


# ================= ORDERS =================

# @login_required
# def order_list(request):
#     orders = Order.objects.all().order_by("-created_at")
#     return render(request, "admin/order_list.html", {"orders": orders})


@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by('-id')
    delivery_persons = DeliveryPerson.objects.all()

    return render(request, 'admin/order_list.html', {
        'orders': orders,
        'delivery_persons': delivery_persons
    })


def assign_order_ajax(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        delivery_id = request.POST.get("delivery_id")

        try:
            order = Order.objects.get(id=order_id)
            delivery = DeliveryPerson.objects.get(id=delivery_id)

            order.delivery_person = delivery
            order.status = "assigned"
            order.save()

            return JsonResponse({"success": True})

        except:
            return JsonResponse({"success": False})

    return JsonResponse({"success": False})


# @login_required
# def accept_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     order.status = "Out for Delivery"
#     order.save()

#     Notification.objects.create(
#         sender=request.user,
#         receiver=order.user,
#         order=order,
#         title="Order Accepted",
#         message=f"Order #{order.id} is out for delivery."
#     )

#     return redirect("adminpanel:order_list")


# @login_required
# def reject_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     order.status = "Rejected"
#     order.save()

#     Notification.objects.create(
#         sender=request.user,
#         receiver=order.user,
#         order=order,
#         title="Order Rejected",
#         message=f"Order #{order.id} has been rejected."
#     )

#     return redirect("adminpanel:order_list")


# ================= NOTIFICATIONS =================

@login_required
def notifications_view(request):
    notes = Notification.objects.filter(
        receiver=request.user
    ).order_by("-id")

    return render(request, "admin/notifications.html", {
        "notifications": notes
    })


@login_required
def mark_notification_read(request, notification_id):
    note = get_object_or_404(
        Notification,
        id=notification_id,
        receiver=request.user
    )
    note.is_read = True
    note.save()
    return redirect("adminpanel:notifications")


# ================= LENS & OFFER =================

@login_required
def lens_list(request):
    return render(request, "admin/lens_list.html", {
        "lenses": Lens.objects.all()
    })


@login_required
def offer_list(request):
    return render(request, "admin/offer_list.html", {
        "offers": Offer.objects.all()
    })


@login_required
def create_offer(request):
    return render(request, "admin/create_offer.html")


def edit_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect("adminpanel:category_list")  # tamara list page nu name mukjo

    return render(request, "adminpanel/edit_category.html", {"category": category})


def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("adminpanel:category_list")  # tamara list page nu name mukjo

def add_subcategory(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")

        category = Category.objects.get(id=category_id)

        SubCategory.objects.create(
            name=name,
            category=category
        )

        messages.success(request, "SubCategory added successfully!")
        return redirect("adminpanel:subcategory_list")  # tamaru list page name mukjo

    return render(request, "adminpanel/add_subcategory.html", {
        "categories": categories
    })

def edit_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        subcategory.name = request.POST.get("name")
        category_id = request.POST.get("category")
        subcategory.category = Category.objects.get(id=category_id)
        subcategory.save()

        messages.success(request, "SubCategory updated successfully!")
        return redirect("adminpanel:subcategory_list")  # tamaru list page name

    return render(request, "adminpanel/edit_subcategory.html", {
        "subcategory": subcategory,
        "categories": categories
    })

def delete_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    subcategory.delete()

    messages.success(request, "SubCategory deleted successfully!")
    return redirect("adminpanel:subcategory_list")  # tamaru list page name mukjo

def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id)

    data = list(subcategories.values("id", "name"))

    return JsonResponse(data, safe=False)

def add_product(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        category = Category.objects.get(id=category_id)
        subcategory = SubCategory.objects.get(id=subcategory_id)

        Product.objects.create(
            name=name,
            price=price,
            category=category,
            subcategory=subcategory
        )

        messages.success(request, "Product added successfully!")
        return redirect("adminpanel:product_list")  # tamaru list page name

    return render(request, "adminpanel/add_product.html", {
        "categories": categories,
        "subcategories": subcategories
    })

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")

        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        product.category = Category.objects.get(id=category_id)
        product.subcategory = SubCategory.objects.get(id=subcategory_id)

        product.save()

        messages.success(request, "Product updated successfully!")
        return redirect("adminpanel:product_list")  # tamaru list page name

    return render(request, "adminpanel/edit_product.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories
    })

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()

    messages.success(request, "Product deleted successfully!")
    return redirect("adminpanel:product_list")  # tamaru list page name mukjo


def delivery_person_list(request):
    delivery_persons = DeliveryPerson.objects.all()
    
    return render(request, "admin/delivery_person_list.html", {
             "delivery_persons": delivery_persons
    })

def add_delivery_person(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("adminpanel:add_delivery_person")

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Add to Delivery group
        delivery_group, created = Group.objects.get_or_create(name="Delivery")
        user.groups.add(delivery_group)

        # 🔥 IMPORTANT — Create DeliveryPerson record
        DeliveryPerson.objects.create(
            user=user,
            phone=phone,
            address=address
        )

        messages.success(request, "Delivery person added successfully!")
        return redirect("adminpanel:delivery_person_list")

    return render(request, "admin/add_delivery_person.html")


def revenue_dashboard(request):
    return render(request, "admin/revenue_dashboard.html")



def user_list(request):
    users = User.objects.all()
    return render(request, "admin/user_list.html", {"users": users})


def low_stock_products(request):
    products = Product.objects.filter(stock__lte=5)  # 5 thi ochho stock
    return render(request, "admin/low_stock.html", {"products": products})

def company_create(
        request):
    if CompanyInfo.objects.exists():
        return redirect("adminpanel:company_update")

    if request.method == "POST":
        CompanyInfo.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            gst_number=request.POST.get("gst_number"),
            logo=request.FILES.get("logo"),
        )
        messages.success(request, "Company Info Added Successfully!")
        return redirect("adminpanel:dashboard")

    return render(request, "admin/company_form.html")


def notifications(request):
    all_notifications = Notification.objects.all().order_by("-created_at")
    return render(request, "admin/notifications.html", {
        "notifications": all_notifications
    })

def add_notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        receiver_id = request.POST.get("receiver")

        receiver = User.objects.get(id=receiver_id)

        Notification.objects.create(
            sender=request.user,
            receiver=receiver,
            title=title,
            message=message
        )

        messages.success(request, "Notification sent successfully!")
        return redirect("adminpanel:notifications")

    users = User.objects.all()
    return render(request, "admin/add_notification.html", {
        "users": users
    })

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                f"/admin-panel/reset-password/{uid}/{token}/"
            )

            send_mail(
                "Password Reset",
                f"Click the link to reset your password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Password reset link sent to your email!")
            return redirect("adminpanel:forgot_password")
        except User.DoesNotExist:
            messages.error(request, "Email not found!")

    return render(request, "admin/forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, "Password reset successfully!")
                return redirect("adminpanel:login")
            else:
                messages.error(request, "Passwords do not match!")

        return render(request, "admin/reset_password.html", {"validlink": True})
    else:
        messages.error(request, "Invalid or expired link.")
        return render(request, "adminreset_password.html", {"validlink": False})
    
def admin_orders(request):
    orders = Order.objects.all()
    delivery_persons = DeliveryPerson.objects.all()

    return render(request, "adminpanel/orders.html", {
        "orders": orders,
        "delivery_persons": delivery_persons
    })

