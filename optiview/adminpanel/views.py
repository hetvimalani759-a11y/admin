from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from .models import Order, DeliveryPerson
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Product, Category, SubCategory,Offer,
    Order,OrderItem, Lens, Notification, CompanyInfo
)

LOW_STOCK_THRESHOLD = 50

# --------------------------- AUTH VIEWS ---------------------------

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            messages.success(request, "Welcome Admin")
            return redirect("adminpanel:dashboard")
        messages.error(request, "Invalid username or password")
    return render(request, "admin/login.html")


@login_required(login_url="adminpanel:login")
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("adminpanel:login")


# --------------------------- DASHBOARD ---------------------------

@login_required(login_url="adminpanel:login")
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_lenses = Lens.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    latest_products = Product.objects.order_by("-created_at")[:1]
    company = CompanyInfo.objects.first()
    monthly_revenue = (
        Order.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    low_stock = Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD).count()

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_lenses": total_lenses,
        "total_revenue": total_revenue,
        "latest_products": latest_products,
        "company": company,
        "total_users": total_users,
        "monthly_revenue": monthly_revenue,
        "revenue_months": [r["month"].strftime("%b %Y") for r in monthly_revenue],
        "revenue_values": [r["total"] for r in monthly_revenue],
        "notifications": notifications,
        "notification_count": notifications.count(),
        "low_stock": low_stock,
    }
    return render(request, "admin/dashboard.html", context)


# --------------------------- NOTIFICATIONS ---------------------------
def apply_discount(products, discount_percent):
    for product in products:
        product.discount_percent = discount_percent
        product.save()

@login_required
def notifications(request):
    notifications = Notification.objects.all().order_by("-id")
    return render(request, "admin/notifications.html", {"notifications": notifications})


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})


@login_required
def add_notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        for user in User.objects.all():
            Notification.objects.create(user=user, title=title, message=message)
        return redirect("adminpanel:notifications")
    return render(request, "admin/add_notification.html")


# --------------------------- CATEGORY VIEWS ---------------------------

@login_required(login_url="adminpanel:login")
def add_category(request):
    categories = Category.objects.all().order_by("-id")
    if request.method == "POST":
        name = request.POST.get("name").strip()
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, "Category added successfully")
        return redirect("adminpanel:add_category")
    return render(request, "admin/add_category.html", {"categories": categories})


@login_required(login_url="adminpanel:login")
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == "POST":
        name = request.POST.get("name").strip()
        if name:
            category.name = name
            category.save()
            messages.success(request, "Category updated successfully")
        return redirect("adminpanel:add_category")
    return render(request, "admin/edit_category.html", {"category": category})


@login_required(login_url="adminpanel:login")
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, "Category deleted successfully")
    return redirect("adminpanel:add_category")


# --------------------------- SUBCATEGORY VIEWS ---------------------------

@login_required
def add_subcategory(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.select_related("category").all()
    if request.method == "POST":
        SubCategory.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name")
        )
        return redirect("adminpanel:add_subcategory")
    return render(request, "admin/add_subcategory.html", {
        "categories": categories,
        "subcategories": subcategories
    })


@login_required(login_url="adminpanel:login")
def edit_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name").strip()
        category_id = request.POST.get("category")
        if name and category_id:
            subcategory.name = name
            subcategory.category_id = category_id
            subcategory.save()
            messages.success(request, "Subcategory updated successfully")
        return redirect("adminpanel:add_subcategory")
    return render(request, "admin/edit_subcategory.html", {
        "subcategory": subcategory,
        "categories": categories
    })


@login_required(login_url="adminpanel:login")
def delete_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully")
    return redirect("adminpanel:add_subcategory")


@login_required
def get_subcategories(request, category_id):
    subcats = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse([{"id": s.id, "name": s.name} for s in subcats], safe=False)


# --------------------------- PRODUCT VIEWS ---------------------------

@login_required(login_url="adminpanel:login")
def product_list(request):
    search = request.GET.get("search", "")
    products = Product.objects.all()
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__icontains=search) |
            Q(price__icontains=search)
        )
    return render(request, "admin/product_list.html", {"products": products, "search": search})


@login_required(login_url="adminpanel:login")
def add_product(request):
    categories = Category.objects.all()
    if request.method == "POST":
        Product.objects.create(
            name=request.POST["name"],
            brand=request.POST["brand"],
            price=request.POST["price"],
            stock=request.POST["stock"],
            category_id=request.POST["category"],
            subcategory_id=request.POST["subcategory"],
            image=request.FILES.get("image")
        )
        # Notify users
        for user in User.objects.filter(is_staff=False):
            Notification.objects.create(user=user, message="New product added!")
        messages.success(request, "Product added successfully")
        return redirect("adminpanel:product_list")
    return render(request, "admin/add_product.html", {"categories": categories})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category=product.category)

    if request.method == "POST":
        product.category_id = request.POST.get('category')
        product.subcategory_id = request.POST.get('subcategory')
        product.name = request.POST.get("name")
        product.brand = request.POST.get("brand")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")
        product.save()
        messages.success(request, "Product updated")
        return redirect("adminpanel:product_list")

    return render(request, "admin/edit_product.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories
    })


@login_required
def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    messages.error(request, "Product deleted")
    return redirect("adminpanel:product_list")


# --------------------------- ORDER VIEWS ---------------------------



@login_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    orderitems = OrderItem.objects.select_related("order", "product")

    return render(request, "admin/order_list.html", {
        "orders": orders,
        "orderitems": orderitems
    })


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
    return redirect('adminpanel:order_list')


# --------------------------- LENS VIEWS ---------------------------

@login_required
def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, "admin/lens_list.html", {"lenses": lenses})


# --------------------------- COMPANY INFO ---------------------------

@login_required
def company_create(request):
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
        messages.success(request, "Company info added")
        return redirect("adminpanel:dashboard")
    return render(request, "admin/company_add.html")


@login_required
def company_update(request):
    company = get_object_or_404(CompanyInfo)
    if request.method == "POST":
        company.name = request.POST.get("name")
        company.email = request.POST.get("email")
        company.phone = request.POST.get("phone")
        company.address = request.POST.get("address")
        company.gst_number = request.POST.get("gst_number")
        if request.FILES.get("logo"):
            company.logo = request.FILES.get("logo")
        company.save()
        messages.success(request, "Company info updated")
        return redirect("adminpanel:dashboard")
    return render(request, "admin/company_edit.html", {"company": company})
# ----------------------------user-------------------------------
@login_required(login_url="adminpanel:login")
def user_list(request):
    users = User.objects.all().order_by("-id")
    return render(request, "admin/user_list.html", {"users": users})
def low_stock_products(request):
    products = Product.objects.filter(stock__lt=LOW_STOCK_THRESHOLD)
    labels = [p.name for p in products]
    data = [p.stock for p in products]

    return render(request, "admin/low_stock_products.html", {
        "products": products,
        "labels": labels,
        "data": data
    })

def revenue_dashboard(request):
    monthly_revenue = (
        Order.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    data = {
        "months": [r["month"].strftime("%b %Y") for r in monthly_revenue],
        "revenues": [r["total"] for r in monthly_revenue],
    }

    return render(request, 'admin/revenue_dashboard.html', data)   



def assign_order(request):
    orders = Order.objects.filter(status='Pending')
    delivery_persons = DeliveryPerson.objects.all()

    if request.method == "POST":
        order_id = request.POST.get("order")
        dp_id = request.POST.get("delivery_person")

        order = Order.objects.get(id=order_id)
        dp = DeliveryPerson.objects.get(id=dp_id)

        order.assigned_to = dp
        order.status = 'Assigned'
        order.save()

        return redirect('assign_order')

    return render(request, 'assign_order.html', {
        'orders': orders,
        'delivery_persons': delivery_persons
    })



@login_required
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("status")

        if new_status:
            order.status = new_status
            order.save()

    return redirect("adminpanel:order_list")


@staff_member_required
def delivery_person_list(request):
    delivery_persons = DeliveryPerson.objects.select_related('user')

    return render(request, 'admin/delivery_person_list.html', {
        'delivery_persons': delivery_persons
    })
# ---------------- CREATE ----------------
def create_offer(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        product_id = request.POST.get('product')
        category_id = request.POST.get('category')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        if product_id and category_id:
            messages.error(request, "Select either Product OR Category.")
            return redirect('create_offer')

        if not product_id and not category_id:
            messages.error(request, "Select at least Product or Category.")
            return redirect('create_offer')

        Offer.objects.create(
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            product_id=product_id or None,
            category_id=category_id or None,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )

        messages.success(request, "Offer created successfully!")
        return redirect('adminpanel:offer_list')

    return render(request, 'admin/create_offer.html', {
        'products': products,
        'categories': categories
    })


# ---------------- LIST ----------------
def offer_list(request):
    offers = Offer.objects.all().order_by('-id')
    return render(request, 'admin/offer_list.html', {'offers': offers})


# ---------------- EDIT ----------------
def edit_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        offer.name = request.POST.get('name')
        offer.discount_type = request.POST.get('discount_type')
        offer.discount_value = request.POST.get('discount_value')
        product_id = request.POST.get('product')
        category_id = request.POST.get('category')
        offer.start_date = request.POST.get('start_date')
        offer.end_date = request.POST.get('end_date')
        offer.is_active = request.POST.get('is_active') == 'on'

        if product_id and category_id:
            messages.error(request, "Select either Product OR Category.")
            return redirect('edit_offer', pk=pk)

        if not product_id and not category_id:
            messages.error(request, "Select at least Product or Category.")
            return redirect('edit_offer', pk=pk)

        offer.product_id = product_id or None
        offer.category_id = category_id or None
        offer.save()

        messages.success(request, "Offer updated successfully!")
        return redirect('adminpanel:offer_list')

    return render(request, 'admin/edit_offer.html', {
        'offer': offer,
        'products': products,
        'categories': categories
    })


# ---------------- DELETE ----------------
def delete_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    offer.delete()
    messages.success(request, "Offer deleted successfully!")
    return redirect('adminpanel:offer_list')
