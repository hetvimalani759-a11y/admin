from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, Prefetch
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User


from .models import (
    Product, Category, SubCategory,
    Order, Lens, Notification, CompanyInfo
)
from .form import CompanyInfoForm

LOW_STOCK_THRESHOLD = 50
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


@login_required(login_url="adminpanel:login")

  # or whatever value you define

def dashboard(request):

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_lenses = Lens.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    latest_products = Product.objects.order_by("-created_at")[:1]

    monthly_revenue = (
        Order.objects
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    notifications = Notification.objects.filter(user=request.user, is_read=False)

    low_stock_products = Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD)

    # Prepare data for Chart.js
    low_stock_names = [p.name for p in low_stock_products]
    low_stock_values = [p.stock for p in low_stock_products]

    # Revenue chart data
    revenue_months = [r["month"].strftime("%b %Y") for r in monthly_revenue]
    revenue_values = [r["total"] for r in monthly_revenue]

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_lenses": total_lenses,
        "latest_products": latest_products,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "notifications": notifications,
        "notification_count": notifications.count(),
        "low_stock_products": low_stock_products,
        "low_stock_names": low_stock_names,
        "low_stock_values": low_stock_values,
        "revenue_months": revenue_months,
        "revenue_values": revenue_values,
    }

    return render(request, "admin/dashboard.html", context)

@login_required
def notifications(request):
    notifications = Notification.objects.all().order_by("-id")
    return render(request, "admin/notifications.html", {
        "notifications": notifications
    })


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True)
    return JsonResponse({"status": "ok"})


@login_required
def add_notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")

        for user in User.objects.all():
            Notification.objects.create(
                user=user,
                title=title,
                message=message
            )
        return redirect("adminpanel:notifications")
    
    return render(request, "admin/add_notification.html")

@login_required(login_url="adminpanel:login")
def add_category(request):
    categories = Category.objects.all().order_by("-id")

    if request.method == "POST":
        name = request.POST.get("name").strip()
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, "Category added successfully")
        return redirect("adminpanel:add_category")

    return render(request, "admin/add_category.html", {
        "categories": categories
    })




@login_required
def add_subcategory(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.select_related("category")

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


def get_subcategories(request, category_id):
    subcats = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse(
        [{"id": s.id, "name": s.name} for s in subcats],
        safe=False
    )
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

    context = {
        "products": products,
        "search": search
    }

    return render(request, "admin/product_list.html", context)
    
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

        # notify users
        for user in User.objects.filter(is_staff=False):
            Notification.objects.create(
                user=user,
                message="New product added!"
            )

        messages.success(request, "Product added successfully")
        return redirect("adminpanel:product_list")

    return render(request, "admin/add_product.html", {
        "categories": categories
    })

@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.brand = request.POST.get("brand")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()
        messages.success(request, "Product updated")
        return redirect("adminpanel:product_list")

    return render(request, "admin/edit_product.html", {"product": product})


@login_required
def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    messages.error(request, "Product deleted")
    return redirect("adminpanel:product_list")
    
@login_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/order_list.html", {"orders": orders})


@login_required
def update_order_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()
    return redirect("adminpanel:order_list")
@login_required
def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, "admin/lens_list.html", {"lenses": lenses})
@login_required
def update_company_info(request):
    company = CompanyInfo.objects.first()
    if not company:
        messages.error(request, "Company info not found")
        return redirect("adminpanel:dashboard")

    if request.method == "POST":
        form = CompanyInfoForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company info updated")
            return redirect("adminpanel:dashboard")
    else:
        form = CompanyInfoForm(instance=company)

    return render(request, "admin/update_company.html", {"form": form})
