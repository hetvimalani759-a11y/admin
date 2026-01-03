from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import *



@login_required(login_url="adminpanel:login")
def dashboard(request):
    ...
def dashboard(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    )

    return render(request, "dashboard.html", {
        "notifications": notifications,
        "notification_count": notifications.count()
    })


from .models import Product, Lens, Order


# ======================
# AUTH
# ======================

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            messages.success(request, "👋 Welcome Admin")
            return redirect('adminpanel:dashboard')
        else:
            messages.error(request, "❌ Invalid username or password")

    return render(request, "admin/login.html")



def mark_notifications_read(request):
    Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True)
    return JsonResponse({"status": "ok"})

from .models import Notification
from django.contrib.auth.models import User

def add_product(request):
    if request.method == "POST":
        # save product logic here...

        users = User.objects.filter(is_staff=False)

        for user in users:
            Notification.objects.create(
                user=user,
                message="New product added! Check it now."
            )

        return redirect("adminpanel:product_list")







@login_required(login_url='adminpanel:login')
def logout_view(request):
    logout(request)
    messages.success(request, "👋Logged out successfully")
   
    return redirect('adminpanel:login')


from django.shortcuts import render
from .models import Notification

def notifications(request):
    notifications = Notification.objects.all().order_by('-id')
    return render(request, 'admin/notifications.html', {
        'notifications': notifications
    })
# ======================
# DASHBOARD
# ======================
from django.db.models import Sum,F
from .models import Product, Order, Lens  
from django.db.models.functions import TruncMonth
# from orders.models import Order   # adjust app name if different
from .models import Product, Notification
LOW_STOCK_THRESHOLD = 50
def create_order(request):
    Order.objects.create(
        user=request.user,
        total_amount=1500,
        status="Pending"
    )
from django.shortcuts import render, redirect
from .models import Order

def add_order(request):
    if request.method == "POST":
        Order.objects.create(
            user=request.user,
            total_amount=request.POST['total_amount'],
            status=request.POST['status']
        )
        return redirect('dashboard')

    return render(request, "admin/add_order.html")
from django.shortcuts import render
from .models import Order

def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, "admin/orders.html", {
        "orders": orders
    })

from django.shortcuts import redirect, get_object_or_404

# @login_required
# def update_order_status(request, order_id):
#     if request.method == "POST":
#         order = get_object_or_404(Order, id=order_id)
#         order.status = request.POST.get("status")
#         order.save()

    # return redirect('order_list')
  # ✅ now this EXISTS

@login_required(login_url="adminpanel:login")

 # adjust names if different

def dashboard(request):
    
    total_products = Product.objects.count()
    total_orders=Order.objects.count()  # or '-created_at'
    total_lenses = Lens.objects.count()
    monthly_revenue = (
        Order.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    revenue_months = [m['month'].strftime('%b %Y') for m in monthly_revenue]
    revenue_values = [float(m['total']) for m in monthly_revenue]
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    latest_products = Product.objects.order_by('-id')[:1]
    company = CompanyInfo.objects.first()
    # Get low stock products
    LOW_STOCK_THRESHOLD = 50  # products with stock <= 5 will trigger low stock alerts
    # rest of your code
    low_stock_products = Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD)
    low_stock_names = [p.name for p in low_stock_products]
    low_stock_values = [p.stock for p in low_stock_products]
    # if request.user.is_authenticated:
    #     for product in low_stock_products:
    #         if not Notification.objects.filter(user=request.user, message__icontains=product.name, is_read=False).exists():
    #             Notification.objects.create(
    #                 user=request.user,
    #                 message=f"Low stock alert: {product.name} only {product.stock} left!"
    #             )

    #     notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # else:
    #     notifications = []
        
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_lenses': total_lenses,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'latest_products': latest_products,
        "company": company,
        "low_stock_products": low_stock_products,
        "low_stock_names": low_stock_names,
        "low_stock_values": low_stock_values,
        'revenue_months': revenue_months,
        'revenue_values': revenue_values,
        "notifications": notifications,
    }

    return render(request, 'admin/dashboard.html', context)
    
    
    
from django.db.models.functions import TruncMonth

monthly_revenue = (
    Order.objects
    .annotate(month=TruncMonth('created_at'))
    .values('month')
    .annotate(total=Sum('total_amount'))
    .order_by('month')
)
from django.shortcuts import render, redirect, get_object_or_404
from .models import CompanyInfo
from .form import*
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def update_company_info(request):
    # Get the first (and only) company info record
    company = CompanyInfo.objects.first()
    if not company:
        messages.error(request, "Company info not found.")
        return redirect('dashboard')

    if request.method == "POST":
        form = CompanyInfoForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company information updated successfully.")
            return redirect('dashboard')
    else:
        form = CompanyInfoForm(instance=company)

    return render(request, 'admin/update_company.html', {'form': form})

# ======================
# PRODUCT CRUD
# ======================

from django.shortcuts import render
from django.db.models import Q
from .models import Product
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




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product

@login_required(login_url='adminpanel:login')
def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"),
            brand=request.POST.get("brand"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
            image=request.FILES.get("image"),
        )

        messages.success(request, "✅ Product added successfully")
        return redirect('adminpanel:product_list')

    return render(request, "admin/add_product.html")



@login_required(login_url='adminpanel:login')
def edit_product(request, id):
    product = Product.objects.get(id=id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.brand = request.POST.get("brand")
        product.price = request.POST.get("price")
        product.stock = int(request.POST.get("stock", 0))

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()  
        if product.stock < LOW_STOCK_THRESHOLD:
            # redirect to dashboard with low stock alert
            messages.warning(request, f"Low stock alert! {product.name} has only {product.stock} items left.")
        else:
            messages.success(request, "✏️ Product updated successfully")
        
        return redirect('adminpanel:product_list')

    return render(request, "admin/edit_product.html", {"product": product})

@login_required(login_url='adminpanel:login')
def delete_product(request, id):
    Product.objects.get(id=id).delete()
    messages.error(request, "🗑️ Product deleted")
    return redirect('adminpanel:product_list')



# ======================
# LENSES
# ======================

@login_required(login_url="adminpanel:login")
def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, "admin/lens_list.html", {"lenses": lenses})


# ======================
# ORDERS
# ======================

@login_required(login_url="adminpanel:login")
def order_list(request):
    orders = Order.objects.all()
    return render(request, "admin/order_list.html", {"orders": orders})

@login_required(login_url="adminpanel:login")
def update_order_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()
    return redirect("order_list")


from .models import Notification
from django.contrib.auth.models import User

def send_notification(user, title, message):
    Notification.objects.create(
        user=user,
        title=title,
        message=message
    )
def add_notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")

        # Send to ALL users
        users = User.objects.all()
        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message
            )
        return redirect('adminpanel:notifications')

    return render(request, 'admin/add_notification.html')